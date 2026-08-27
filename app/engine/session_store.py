"""
KSP Sentinel AI — DuckDB Session-Isolated Storage (SOLID: DIP)
"""
import logging
import re
import tempfile
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import duckdb

from app.core.interfaces import IDatasetRepository

log = logging.getLogger("standalone.session_store")


class SessionDataStore(IDatasetRepository):
    """
    Manages session-isolated in-memory DuckDB database sessions.
    Enforces Data-Empty baseline until an officer uploads a CSV/Excel file.
    Thread-safe implementation using threading.RLock().
    """
    def __init__(self):
        self.sessions: Dict[str, dict] = {}  # session_id -> { "con": duckdb_con, "tables": {}, "files": [] }
        self._lock = threading.RLock()

    def get_connection(self, session_id: str):
        with self._lock:
            if session_id not in self.sessions:
                con = duckdb.connect(database=":memory:")
                self.sessions[session_id] = {
                    "con": con,
                    "tables": {},
                    "files": []
                }
            return self.sessions[session_id]["con"]

    def ingest_csv(self, session_id: str, filename: str, csv_bytes: bytes) -> dict:
        con = self.get_connection(session_id)
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp.write(csv_bytes)
            tmp_path = tmp.name

        try:
            # Multi-Dataset Coexistence: Derive dedicated table name from filename
            clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', Path(filename).stem).lower().strip('_')
            
            # Primary default is crime_dataset unless already occupied
            with self._lock:
                has_primary = "crime_dataset" in self.sessions[session_id]["tables"]
            
            table_name = "crime_dataset" if not has_primary else f"table_{clean_name}"
            
            con.execute(f"DROP TABLE IF EXISTS {table_name}")
            con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{tmp_path}')")

            # If network dataset, also create alias network_dataset
            if any(w in clean_name for w in ["network", "mule", "cdr", "telecom", "link", "syndicate"]):
                con.execute("DROP TABLE IF EXISTS network_dataset")
                con.execute(f"CREATE TABLE network_dataset AS SELECT * FROM {table_name}")

            row_count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            desc = con.execute(f"DESCRIBE {table_name}").fetchall()
            columns = [row[0] for row in desc]

            with self._lock:
                table_meta = {
                    "filename": filename,
                    "row_count": row_count,
                    "columns": columns,
                    "schema": desc
                }
                self.sessions[session_id]["tables"][table_name] = table_meta
                if any(w in clean_name for w in ["network", "mule", "cdr", "telecom", "link", "syndicate"]):
                    self.sessions[session_id]["tables"]["network_dataset"] = table_meta

                # Track currently active visual table for dynamic Visual Studio re-binding
                self.sessions[session_id]["active_visual_table"] = table_name

                # Prevent duplicate file entries
                if not any(f["name"] == filename for f in self.sessions[session_id]["files"]):
                    self.sessions[session_id]["files"].append({
                        "name": filename,
                        "table_name": table_name,
                        "size": len(csv_bytes),
                        "rows": row_count
                    })

            log.info(f"[SessionDataStore] Ingested {filename} -> {table_name} ({row_count} rows, {len(columns)} cols) in session '{session_id}' (Active Visual Table: '{table_name}')")
            return {
                "success": True,
                "table_name": table_name,
                "row_count": row_count,
                "columns": columns,
                "active_tables": list(self.sessions[session_id]["tables"].keys()),
                "active_visual_table": table_name
            }
        except Exception as e:
            log.error(f"[SessionDataStore] CSV ingestion failed for session '{session_id}': {e}")
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
            if session_id not in self.sessions or not self.sessions[session_id]["tables"]:
                return "crime_dataset"

            tables = self.sessions[session_id]["tables"]
            q_lower = query.lower()

            # Relational / Network indicators
            network_tokens = ["mule", "upi", "phone", "suspect", "vehicle", "cdr", "account", "burner", "nexus", "kingpin", "hub", "chain"]
            if any(t in q_lower for t in network_tokens):
                if "network_dataset" in tables:
                    return "network_dataset"
                for tname, tmeta in tables.items():
                    cols_lower = [c.lower() for c in tmeta.get("columns", [])]
                    if any(w in cols_lower for w in ["suspect_name", "phone_number", "upi_id", "vehicle_number", "bank_account"]):
                        return tname

            # Default to active visual table or primary table
            return self.get_active_visual_table(session_id) or "crime_dataset"

    def has_dataset(self, session_id: str, table_name: Optional[str] = None) -> bool:
        with self._lock:
            if session_id not in self.sessions:
                return False
            tables = self.sessions[session_id]["tables"]
            if table_name:
                return table_name in tables
            return len(tables) > 0

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
        con = self.get_connection(session_id)
        try:
            rel = con.execute(query)
            cols = [desc[0] for desc in rel.description] if rel.description else []
            rows = rel.fetchall()
            return cols, rows
        except Exception as e:
            log.error(f"[SessionDataStore] SQL execution error: {e} | Query: {query}")
            raise e


# Singleton Store
session_store = SessionDataStore()
