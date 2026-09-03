"""
KSP Sentinel AI — SQLite Session-Isolated Storage (SOLID: DIP + SRP)
Pure-Python, C-extension free, thread-safe session database engine.
"""
import csv
import io
import json
import logging
import os
import re
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.core.interfaces import IDatasetRepository
from app.providers.orchestrator import orchestrator

log = logging.getLogger("standalone.session_store")


class SQLiteSessionStore(IDatasetRepository):
    """
    Manages session-isolated in-memory SQLite database sessions.
    Enforces Data-Empty baseline until an officer uploads a CSV/Excel/JSON file.
    Thread-safe implementation using threading.RLock().
    """
    def __init__(self):
        self.sessions: Dict[str, dict] = {}  # session_id -> { "con": sqlite_con, "tables": {}, "files": [] }
        self._lock = threading.RLock()
        self.storage_dir = Path(os.getenv("SESSION_STORAGE_DIR", os.path.join(os.getcwd(), "data_store", "sessions")))
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            log.warning(f"[SessionDataStore] Could not create storage dir: {e}")

    def get_connection(self, session_id: str) -> sqlite3.Connection:
        with self._lock:
            if session_id not in self.sessions:
                safe_id = re.sub(r'[^a-zA-Z0-9_\-]', '_', str(session_id))
                db_path = self.storage_dir / f"{safe_id}.sqlite"
                con = sqlite3.connect(str(db_path), check_same_thread=False)
                con.isolation_level = None  # Autocommit mode
                self.sessions[session_id] = {
                    "con": con,
                    "tables": {},
                    "files": [],
                    "db_path": str(db_path)
                }
                # Auto-restore existing tables if the database already exists on disk
                try:
                    tables = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
                    for t_row in tables:
                        t_name = t_row[0]
                        pragma = con.execute(f'PRAGMA table_info("{t_name}")').fetchall()
                        desc = [(p[1], p[2]) for p in pragma]
                        columns = [p[1] for p in pragma]
                        row_count = con.execute(f'SELECT COUNT(*) FROM "{t_name}"').fetchone()[0]
                        self.sessions[session_id]["tables"][t_name] = {
                            "filename": t_name,
                            "row_count": row_count,
                            "columns": columns,
                            "schema": desc,
                            "classification": "ANALYTICAL"
                        }
                    if tables:
                        self.sessions[session_id]["active_visual_table"] = tables[0][0]
                        log.info(f"[SessionDataStore] 🔄 Auto-restored {len(tables)} tables from disk for session '{session_id}'")
                except Exception as e:
                    log.debug(f"[SessionDataStore] Table restoration notice: {e}")
            return self.sessions[session_id]["con"]

    def rehydrate_session(self, session_id: str) -> bool:
        """
        Attempts to transparently restore an SQLite database for session_id
        from local disk or downloading its dataset BLOB from Catalyst File Store.
        """
        if not session_id:
            return False

        with self._lock:
            if session_id in self.sessions and self.sessions[session_id].get("tables"):
                return True

        # First attempt local disk rehydration via get_connection
        self.get_connection(session_id)
        with self._lock:
            if session_id in self.sessions and self.sessions[session_id].get("tables"):
                return True

        try:
            from app.services.catalyst_service import catalyst_filestore_service
            blob_info = catalyst_filestore_service.download_session_dataset(session_id)
            if blob_info:
                filename, file_bytes = blob_info
                log.info(f"[SessionDataStore] 🔄 Rehydrating session '{session_id}' from Catalyst File Store ({filename}, {len(file_bytes)} bytes)...")
                self.ingest_dataset(session_id, filename, file_bytes, upload_to_cloud=False)
                return True
        except Exception as e:
            log.warning(f"[SessionDataStore] Session rehydration attempt failed for '{session_id}': {e}")
        return False

    def _infer_and_convert_rows(self, raw_rows: List[List[Any]], headers: List[str]) -> Tuple[List[str], List[List[Any]]]:
        """
        Dynamically infers SQLite column types (INTEGER, REAL, TEXT) from sample values
        and converts string representations into native Python types for parameterized insertion.
        """
        if not raw_rows:
            return ["TEXT"] * len(headers), []

        sample_size = min(len(raw_rows), 100)
        sample = raw_rows[:sample_size]
        inferred_types: List[str] = []

        for col_idx in range(len(headers)):
            col_values = [r[col_idx] for r in sample if col_idx < len(r) and r[col_idx] is not None and str(r[col_idx]).strip() != ""]
            if not col_values:
                inferred_types.append("TEXT")
                continue

            # Check if all values can be integer
            is_int = True
            for v in col_values:
                try:
                    int_val = int(str(v).replace(",", ""))
                except (ValueError, TypeError):
                    is_int = False
                    break
            if is_int:
                inferred_types.append("INTEGER")
                continue

            # Check if all values can be float
            is_real = True
            for v in col_values:
                try:
                    float_val = float(str(v).replace(",", ""))
                except (ValueError, TypeError):
                    is_real = False
                    break
            if is_real:
                inferred_types.append("REAL")
                continue

            inferred_types.append("TEXT")

        # Convert all rows based on inferred types
        converted_rows: List[List[Any]] = []
        for r in raw_rows:
            row_converted = []
            for col_idx in range(len(headers)):
                val = r[col_idx] if col_idx < len(r) else None
                if val is None or str(val).strip() == "":
                    row_converted.append(None)
                    continue

                col_type = inferred_types[col_idx]
                str_val = str(val).strip()
                if col_type == "INTEGER":
                    try:
                        row_converted.append(int(str_val.replace(",", "")))
                    except Exception:
                        row_converted.append(str_val)
                elif col_type == "REAL":
                    try:
                        row_converted.append(float(str_val.replace(",", "")))
                    except Exception:
                        row_converted.append(str_val)
                else:
                    row_converted.append(str_val)
            converted_rows.append(row_converted)

        return inferred_types, converted_rows

    def _parse_file_data(self, filename: str, file_bytes: bytes) -> Tuple[List[str], List[List[Any]]]:
        """
        Pure-Python ingestion for CSV, JSON, and Excel without C-extension dependencies.
        """
        suffix = Path(filename).suffix.lower()

        # 1. JSON Format
        if suffix == ".json":
            text = file_bytes.decode("utf-8", errors="replace")
            parsed = json.loads(text)
            records = []
            if isinstance(parsed, list):
                records = parsed
            elif isinstance(parsed, dict):
                for key in ["data", "records", "rows", "items", "cases", "crimes"]:
                    if key in parsed and isinstance(parsed[key], list):
                        records = parsed[key]
                        break
                if not records:
                    records = [parsed]

            if not records:
                return ["id"], []

            headers = list({k: True for rec in records if isinstance(rec, dict) for k in rec.keys()}.keys())
            raw_rows = []
            for rec in records:
                if isinstance(rec, dict):
                    raw_rows.append([rec.get(h) for h in headers])
                else:
                    raw_rows.append([rec])
            return headers, raw_rows

        # 2. Excel Format (.xlsx, .xls)
        elif suffix in (".xlsx", ".xls"):
            try:
                import openpyxl
                wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
                sheet = wb.active
                rows = list(sheet.iter_rows(values_only=True))
                if not rows:
                    return ["col_1"], []
                headers = [str(c or f"col_{idx+1}").strip() for idx, c in enumerate(rows[0])]
                raw_rows = [list(r) for r in rows[1:] if any(c is not None for c in r)]
                return headers, raw_rows
            except Exception as e:
                log.warning(f"[SessionDataStore] openpyxl extraction fallback: {e}")
                # Fall through to CSV parsing

        # 3. SQL Dump Format (.sql)
        elif suffix == ".sql":
            text = file_bytes.decode("utf-8", errors="replace")
            scratch_con = sqlite3.connect(":memory:")
            try:
                clean_sql = re.sub(r'ENGINE\s*=\s*\w+', '', text, flags=re.IGNORECASE)
                clean_sql = re.sub(r'AUTO_INCREMENT\s*=\s*\d+', '', clean_sql, flags=re.IGNORECASE)
                clean_sql = re.sub(r'AUTO_INCREMENT', '', clean_sql, flags=re.IGNORECASE)
                clean_sql = re.sub(r'CHARACTER\s+SET\s+\w+', '', clean_sql, flags=re.IGNORECASE)
                clean_sql = re.sub(r'COLLATE\s+\w+', '', clean_sql, flags=re.IGNORECASE)
                clean_sql = re.sub(r'DEFAULT\s+CHARSET\s*=\s*\w+', '', clean_sql, flags=re.IGNORECASE)
                scratch_con.executescript(clean_sql)
                tables = [r[0] for r in scratch_con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]
                if tables:
                    target_table = tables[0]
                    cur = scratch_con.execute(f'SELECT * FROM "{target_table}"')
                    headers = [d[0] for d in cur.description] if cur.description else ["id"]
                    raw_rows = [list(r) for r in cur.fetchall()]
                    return headers, raw_rows
            except Exception as e:
                log.warning(f"[SessionDataStore] SQL script scratch execution fallback: {e}")
            finally:
                scratch_con.close()

            # Regex fallback for INSERT INTO statements
            insert_matches = re.findall(r'INSERT\s+INTO\s+[`"\[]?(\w+)[`"\]]?\s*(?:\(([^)]+)\))?\s*VALUES\s*(.+?);', text, flags=re.IGNORECASE | re.DOTALL)
            if insert_matches:
                first_match = insert_matches[0]
                headers = [c.strip(" `\"'[]") for c in first_match[1].split(",")] if first_match[1] else []
                raw_rows = []
                val_tuples = re.findall(r'\(([^)]+)\)', first_match[2])
                for vt in val_tuples:
                    row = [v.strip(" '\"") for v in vt.split(",")]
                    raw_rows.append(row)
                if not headers and raw_rows:
                    headers = [f"col_{i+1}" for i in range(len(raw_rows[0]))]
                if headers and raw_rows:
                    return headers, raw_rows

            return ["col_1"], []

        # 4. CSV / Plain text (Default)
        text = file_bytes.decode("utf-8", errors="replace")
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
        if not rows:
            return ["col_1"], []

        raw_headers = rows[0]
        headers = []
        seen_headers = set()
        for idx, h in enumerate(raw_headers):
            clean = re.sub(r'[^a-zA-Z0-9_]', '_', str(h).strip()).strip('_')
            if not clean:
                clean = f"col_{idx+1}"
            original = clean
            dup_idx = 1
            while clean in seen_headers:
                clean = f"{original}_{dup_idx}"
                dup_idx += 1
            seen_headers.add(clean)
            headers.append(clean)

        raw_rows = [r for r in rows[1:] if any(c.strip() for c in r)]
        return headers, raw_rows

    def ingest_dataset(self, session_id: str, filename: str, file_bytes: bytes, upload_to_cloud: bool = True, dataset_purpose: str = "auto") -> dict:
        """
        Polymorphic Ingestion for CSV, JSON, and Excel files into SQLite.
        Applies explicit routing via dataset_purpose or dynamic LLM Schema-Sniffing.
        When upload_to_cloud is True, asynchronously streams the BLOB to Catalyst File Store.
        """
        con = self.get_connection(session_id)
        
        try:
            # ── 1. Target Slot Resolution [Tri-Modal Routing] ─────────────────
            clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', Path(filename).stem).lower().strip('_')
            if not clean_name:
                clean_name = "custom_dataset"
            
            if dataset_purpose == "analytics":
                table_name = "crime_dataset"
            elif dataset_purpose == "network":
                table_name = "network_dataset"
            elif dataset_purpose == "spatial":
                table_name = "spatial_dataset"
            else:
                with self._lock:
                    has_primary = "crime_dataset" in self.sessions[session_id]["tables"]
                table_name = "crime_dataset" if not has_primary else f"table_{clean_name}"
                
            con.execute(f'DROP TABLE IF EXISTS "{table_name}"')

            # ── 1. Pure-Python File Ingestion & Dynamic Schema Inference ──────
            headers, raw_rows = self._parse_file_data(filename, file_bytes)
            inferred_types, converted_rows = self._infer_and_convert_rows(raw_rows, headers)

            cols_def = ", ".join([f'"{col}" {col_type}' for col, col_type in zip(headers, inferred_types)])
            con.execute(f'CREATE TABLE "{table_name}" ({cols_def})')

            if converted_rows:
                placeholders = ", ".join(["?"] * len(headers))
                con.executemany(f'INSERT INTO "{table_name}" VALUES ({placeholders})', converted_rows)

            row_count = con.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0]
            pragma = con.execute(f'PRAGMA table_info("{table_name}")').fetchall()
            desc = [(p[1], p[2]) for p in pragma]
            columns = [p[1] for p in pragma]

            # ── 2. Universal LLM Schema-Sniffing (No Hardcoding) ──────────────
            if dataset_purpose != "auto":
                classification = "GRAPH" if dataset_purpose == "network" else "ANALYTICAL" if dataset_purpose == "analytics" else "SPATIAL"
                log.info(f"[SessionDataStore] Explicit Schema Classification via UI: [{classification}]")
            else:
                prompt = (
                    f"You are a police data router. Review these dataset columns: {columns}.\n"
                    f"- If they represent relational links, transactions, or network entities (e.g. source, target, phone, upi, mule, sender, receiver, account, suspect), reply 'GRAPH'.\n"
                    f"- If they represent statistical metrics, crimes, dates, amounts, or incident aggregations (e.g. fir, date, ipc, crime_type, amount, loss, recovery, station), reply 'ANALYTICAL'.\n"
                    f"- If they represent both or generic multi-domain data, reply 'DUAL'.\n"
                    f"Reply with exactly ONE word: GRAPH, ANALYTICAL, or DUAL."
                )
                try:
                    raw_classification = orchestrator.generate_completion(
                        prompt,
                        system_instruction="You are a dataset schema classifier. Reply with exactly one word: GRAPH, ANALYTICAL, or DUAL.",
                        max_tokens=15
                    ).strip().upper()
                    classification = raw_classification.split()[0].rstrip(".,:") if raw_classification else "DUAL"
                except Exception as e:
                    log.warning(f"[SessionDataStore] LLM schema classification error: {e}. Defaulting to DUAL")
                    classification = "DUAL"

                log.info(f"[SessionDataStore] LLM Schema Classification for '{filename}': [{classification}] ({row_count} rows, {len(columns)} cols)")

            # ── 3. Relational Alias Binding ───────────────────────────────────
            if (classification in ("GRAPH", "DUAL") or any(w in clean_name for w in ["network", "mule", "cdr", "telecom", "link", "syndicate"])) and table_name != "network_dataset":
                con.execute('DROP TABLE IF EXISTS "network_dataset"')
                con.execute(f'CREATE TABLE "network_dataset" AS SELECT * FROM "{table_name}"')

            with self._lock:
                table_meta = {
                    "filename": filename,
                    "row_count": row_count,
                    "columns": columns,
                    "schema": desc,
                    "classification": classification
                }
                self.sessions[session_id]["tables"][table_name] = table_meta
                if classification in ("GRAPH", "DUAL") or any(w in clean_name for w in ["network", "mule", "cdr", "telecom", "link", "syndicate"]):
                    self.sessions[session_id]["tables"]["network_dataset"] = table_meta

                # Track currently active visual table for dynamic Visual Studio re-binding
                self.sessions[session_id]["active_visual_table"] = table_name

                # Prevent duplicate file entries
                if not any(f["name"] == filename for f in self.sessions[session_id]["files"]):
                    self.sessions[session_id]["files"].append({
                        "name": filename,
                        "table_name": table_name,
                        "size": len(file_bytes),
                        "rows": row_count,
                        "classification": classification
                    })

            # ── 4. Asynchronous Cloud Persistence to Catalyst File Store ─────
            if upload_to_cloud:
                try:
                    from app.services.catalyst_service import catalyst_filestore_service
                    catalyst_filestore_service.upload_session_dataset(session_id, filename, file_bytes)
                except Exception as e:
                    log.debug(f"[SessionDataStore] Cloud File Store upload dispatch notice: {e}")

            log.info(f"[SessionDataStore] Ingested {filename} -> {table_name} [{classification}] ({row_count} rows) in SQLite session '{session_id}'")
            return {
                "success": True,
                "table_name": table_name,
                "row_count": row_count,
                "columns": columns,
                "classification": classification,
                "active_tables": list(self.sessions[session_id]["tables"].keys()),
                "active_visual_table": table_name
            }
        except Exception as e:
            log.error(f"[SessionDataStore] Ingestion failed for session '{session_id}' file '{filename}': {e}")
            raise e

    def ingest_csv(self, session_id: str, filename: str, csv_bytes: bytes) -> dict:
        """Backwards-compatible alias for ingest_dataset."""
        return self.ingest_dataset(session_id, filename, csv_bytes)

    def attach_live_database(self, session_id: str, db_type: str, uri: str, table_or_collection: Optional[str] = None, dataset_purpose: str = "auto") -> dict:
        """
        SOLID LSP + OCP: Connects to live enterprise databases (Postgres, MySQL, Mongo, SQLite)
        using pure-Python adapters, extracts up to 5,000 records ephemerally, and streams them
        into an isolated SQLite session slot.
        """
        from app.engine.database_adapters import DatabaseAdapterFactory

        con = self.get_connection(session_id)
        target_entity = (table_or_collection or "cases").strip()
        clean_target = re.sub(r'[^a-zA-Z0-9_]', '_', target_entity).lower().strip('_') or "dataset"

        # ── 1. Target Slot Resolution [Tri-Modal Routing] ─────────────────────
        if dataset_purpose == "analytics":
            table_name = "crime_dataset"
        elif dataset_purpose == "network":
            table_name = "network_dataset"
        elif dataset_purpose == "spatial":
            table_name = "spatial_dataset"
        else:
            with self._lock:
                has_primary = "crime_dataset" in self.sessions[session_id]["tables"]
            table_name = "crime_dataset" if not has_primary else f"live_{db_type.lower()}_{clean_target}"

        try:
            adapter = DatabaseAdapterFactory.get_adapter(db_type)
            headers, raw_rows = adapter.fetch_data(uri, target=target_entity, limit=5000)

            con.execute(f'DROP TABLE IF EXISTS "{table_name}"')
            inferred_types, converted_rows = self._infer_and_convert_rows(raw_rows, headers)

            cols_def = ", ".join([f'"{col}" {col_type}' for col, col_type in zip(headers, inferred_types)])
            con.execute(f'CREATE TABLE "{table_name}" ({cols_def})')

            if converted_rows:
                placeholders = ", ".join(["?"] * len(headers))
                con.executemany(f'INSERT INTO "{table_name}" VALUES ({placeholders})', converted_rows)

            row_count = con.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0]
            pragma = con.execute(f'PRAGMA table_info("{table_name}")').fetchall()
            desc = [(p[1], p[2]) for p in pragma]
            columns = [p[1] for p in pragma]

            # Determine classification
            classification = "GRAPH" if dataset_purpose == "network" else "SPATIAL" if dataset_purpose == "spatial" else "ANALYTICAL" if dataset_purpose == "analytics" else "DUAL"

            if (classification in ("GRAPH", "DUAL") or any(w in clean_target for w in ["network", "mule", "cdr", "telecom", "link", "syndicate"])) and table_name != "network_dataset":
                con.execute('DROP TABLE IF EXISTS "network_dataset"')
                con.execute(f'CREATE TABLE "network_dataset" AS SELECT * FROM "{table_name}"')

            display_name = f"LIVE_{db_type.upper()}:{target_entity}"
            with self._lock:
                table_meta = {
                    "filename": display_name,
                    "row_count": row_count,
                    "columns": columns,
                    "schema": desc,
                    "classification": classification
                }
                self.sessions[session_id]["tables"][table_name] = table_meta
                if classification in ("GRAPH", "DUAL"):
                    self.sessions[session_id]["tables"]["network_dataset"] = table_meta

                self.sessions[session_id]["active_visual_table"] = table_name

                if not any(f["name"] == display_name for f in self.sessions[session_id]["files"]):
                    self.sessions[session_id]["files"].append({
                        "name": display_name,
                        "table_name": table_name,
                        "size": 0,
                        "rows": row_count,
                        "classification": classification
                    })

            log.info(f"[SessionDataStore] Attached live {db_type.upper()} ({target_entity}) -> {table_name} ({row_count} rows) in session '{session_id}'")
            return {
                "success": True,
                "table_name": table_name,
                "row_count": row_count,
                "columns": columns,
                "classification": classification,
                "active_tables": list(self.sessions[session_id]["tables"].keys()),
                "active_visual_table": table_name
            }
        except Exception as e:
            log.error(f"[SessionDataStore] Live database attachment failed for session '{session_id}': {e}")
            raise e

    def get_active_visual_table(self, session_id: str) -> Optional[str]:
        with self._lock:
            if session_id not in self.sessions:
                return None
            return self.sessions[session_id].get("active_visual_table") or (list(self.sessions[session_id]["tables"].keys())[-1] if self.sessions[session_id]["tables"] else None)

    def set_active_visual_table(self, session_id: str, table_name: str):
        with self._lock:
            if session_id in self.sessions and table_name in self.sessions[session_id]["tables"]:
                self.sessions[session_id]["active_visual_table"] = table_name

    def get_table_for_query(self, session_id: str, query: str) -> str:
        with self._lock:
            has_tables = session_id in self.sessions and bool(self.sessions[session_id]["tables"])
            
        if not has_tables:
            self.rehydrate_session(session_id)

        with self._lock:
            if session_id not in self.sessions or not self.sessions[session_id]["tables"]:
                return "crime_dataset"

            tables = self.sessions[session_id]["tables"]
            q_lower = query.lower()

            # 1. Relational / Network indicators
            network_tokens = ["mule", "upi", "phone", "suspect", "vehicle", "cdr", "account", "burner", "nexus", "kingpin", "hub", "chain", "transaction"]
            if any(t in q_lower for t in network_tokens):
                if "network_dataset" in tables:
                    return "network_dataset"
                for tname, tmeta in tables.items():
                    cols_lower = [c.lower() for c in tmeta.get("columns", [])]
                    if any(w in cols_lower for w in ["suspect_name", "phone_number", "upi_id", "vehicle_number", "bank_account", "source", "target"]):
                        return tname

            # 2. Geospatial indicators
            spatial_tokens = ["latitude", "longitude", "lat", "lon", "gps", "coordinate", "hotspot", "gis", "map", "polygon", "spatial", "radius", "boundary", "corridor"]
            if any(t in q_lower for t in spatial_tokens):
                if "spatial_dataset" in tables:
                    return "spatial_dataset"
                for tname, tmeta in tables.items():
                    cols_lower = [c.lower() for c in tmeta.get("columns", [])]
                    if any(w in cols_lower for w in ["latitude", "longitude", "lat", "long", "coordinates", "geom"]):
                        return tname

            # 3. Statistical / Crime indicators or Primary slot
            if "crime_dataset" in tables:
                return "crime_dataset"

            # Default to active visual table or primary table
            return self.get_active_visual_table(session_id) or "crime_dataset"

    def has_dataset(self, session_id: str, table_name: Optional[str] = None) -> bool:
        with self._lock:
            if session_id in self.sessions and self.sessions[session_id]["tables"]:
                if table_name:
                    return table_name in self.sessions[session_id]["tables"]
                return len(self.sessions[session_id]["tables"]) > 0

        # Attempt cloud rehydration on cache-miss
        if self.rehydrate_session(session_id):
            with self._lock:
                if session_id in self.sessions and self.sessions[session_id]["tables"]:
                    if table_name:
                        return table_name in self.sessions[session_id]["tables"]
                    return len(self.sessions[session_id]["tables"]) > 0
        return False

    def get_columns(self, session_id: str, table_name: Optional[str] = None) -> Tuple[List[str], List[str]]:
        if not self.has_dataset(session_id):
            return [], []
        with self._lock:
            tables = self.sessions[session_id]["tables"]
            target_table = table_name if (table_name and table_name in tables) else self.get_active_visual_table(session_id)
            if not target_table or target_table not in tables:
                target_table = list(tables.keys())[0]
            meta = tables.get(target_table, {})
            columns = meta.get("columns", [])
            types = [r[1] for r in meta.get("schema", [])]
            return columns, types

    def get_schema_summary(self, session_id: str, table_name: Optional[str] = None) -> str:
        if not self.has_dataset(session_id):
            return "No dataset active in current session."
        columns, types = self.get_columns(session_id, table_name)
        active_t = self.get_active_visual_table(session_id) or "primary"
        return f"Active Table '{active_t}' ({len(columns)} columns): " + ", ".join([f"{c} ({t})" for c, t in zip(columns, types)])

    def execute_sql(self, session_id: str, query: str) -> Tuple[List[str], List[tuple]]:
        with self._lock:
            has_tables = session_id in self.sessions and bool(self.sessions[session_id]["tables"])
            
        if not has_tables:
            self.rehydrate_session(session_id)

        con = self.get_connection(session_id)
        try:
            cur = con.cursor()
            cur.execute(query)
            cols = [desc[0] for desc in cur.description] if cur.description else []
            rows = cur.fetchall()
            return cols, rows
        except Exception as e:
            log.error(f"[SessionDataStore] SQLite execution error: {e} | Query: {query}")
            raise e


# Backward-compatible aliases and Singleton instance
SessionDataStore = SQLiteSessionStore
session_store = SQLiteSessionStore()
