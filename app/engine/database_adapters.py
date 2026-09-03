"""
KSP Sentinel AI — Enterprise Database Adapters (SOLID: LSP + OCP + SRP)
=======================================================================
Pure-Python, C-extension free database connectivity layer with built-in
SSRF guards and ephemeral query lifecycles for Zoho Catalyst AppSail.

Supported engines:
- PostgreSQL (pg8000 - pure Python)
- MySQL / MariaDB (PyMySQL - pure Python)
- MongoDB (pymongo - pure Python client)
- SQLite3 (sqlite3 standard library)
"""
import ipaddress
import logging
import re
import socket
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, unquote, urlparse

log = logging.getLogger("standalone.db_adapters")


# ── SSRF Guard & Security Validation ──────────────────────────────────────────
class SecurityViolationError(Exception):
    """Raised when an outbound connection string violates SSRF or security rules."""
    pass


def validate_connection_target(hostname: str, port: Optional[int] = None) -> None:
    """
    Prevents Server-Side Request Forgery (SSRF) against cloud metadata endpoints
    and local loopback services.
    """
    if not hostname:
        raise SecurityViolationError("Database hostname/target cannot be empty.")

    clean_host = hostname.strip().lower()

    # Block well-known cloud metadata services and localhost strings
    blocked_hosts = {
        "localhost", "127.0.0.1", "::1", "0.0.0.0",
        "metadata.google.internal", "instance-data",
        "169.254.169.254", "metadata.azure.internal"
    }
    if clean_host in blocked_hosts:
        raise SecurityViolationError(f"Security Alert: Target host '{clean_host}' is blocked for SSRF protection.")

    # Try resolving IP address to detect internal/link-local addresses
    try:
        ip_str = socket.gethostbyname(clean_host)
        ip = ipaddress.ip_address(ip_str)
        if ip.is_loopback:
            raise SecurityViolationError(f"Security Alert: Host resolved to loopback address ({ip_str}).")
        if ip.is_link_local:
            raise SecurityViolationError(f"Security Alert: Host resolved to link-local/cloud metadata ({ip_str}).")
    except socket.gaierror:
        # DNS resolution failure will be caught naturally during connect
        pass


# ── Abstract Base Adapter (LSP + ISP) ─────────────────────────────────────────
class ILiveDatabaseAdapter(ABC):
    """Base interface for all live database extractors."""

    @abstractmethod
    def fetch_data(self, uri: str, target: str, limit: int = 5000) -> Tuple[List[str], List[List[Any]]]:
        """
        Connects ephemerally, fetches up to `limit` records, and returns (columns, rows).
        Guarantees complete connection closure upon exit.
        """
        pass


# ── PostgreSQL Adapter (pg8000 - Pure Python) ──────────────────────────────────
class PostgresAdapter(ILiveDatabaseAdapter):
    """Extracts tables from PostgreSQL using pure-Python pg8000 (No C libpq dependency)."""

    def fetch_data(self, uri: str, target: str, limit: int = 5000) -> Tuple[List[str], List[List[Any]]]:
        try:
            import pg8000.native
        except ImportError:
            raise RuntimeError("pg8000 driver is required for PostgreSQL. Run: pip install pg8000")

        # Sanitize target table name to prevent SQL injection
        clean_table = re.sub(r'[^a-zA-Z0-9_.]', '', target.strip())
        if not clean_table:
            raise ValueError("Invalid or empty target table name.")

        parsed = urlparse(uri)
        hostname = parsed.hostname or "localhost"
        port = parsed.port or 5432
        database = parsed.path.lstrip("/") or "postgres"
        user = unquote(parsed.username or "")
        password = unquote(parsed.password or "")

        validate_connection_target(hostname, port)

        log.info(f"[PostgresAdapter] Ephemeral query to {hostname}:{port}/{database} -> table '{clean_table}'")
        con = None
        try:
            con = pg8000.native.Connection(
                user=user,
                host=hostname,
                port=port,
                database=database,
                password=password,
                timeout=5  # 5s strict timeout
            )
            query = f'SELECT * FROM "{clean_table}" LIMIT {int(limit)}'
            result = con.run(query)

            columns = [col["name"] for col in con.columns] if hasattr(con, "columns") and con.columns else []
            if not columns and result:
                columns = [f"col_{i+1}" for i in range(len(result[0]))]

            rows = [list(r) for r in result]
            return columns, rows
        finally:
            if con:
                try:
                    con.close()
                except Exception:
                    pass


# ── MySQL Adapter (PyMySQL - Pure Python) ──────────────────────────────────────
class MySQLAdapter(ILiveDatabaseAdapter):
    """Extracts tables from MySQL / MariaDB using pure-Python PyMySQL (No gcc/mysqlclient dependency)."""

    def fetch_data(self, uri: str, target: str, limit: int = 5000) -> Tuple[List[str], List[List[Any]]]:
        try:
            import pymysql
        except ImportError:
            raise RuntimeError("PyMySQL driver is required for MySQL. Run: pip install pymysql")

        clean_table = re.sub(r'[^a-zA-Z0-9_]', '', target.strip())
        if not clean_table:
            raise ValueError("Invalid or empty target table name.")

        parsed = urlparse(uri)
        hostname = parsed.hostname or "localhost"
        port = parsed.port or 3306
        database = parsed.path.lstrip("/") or ""
        user = unquote(parsed.username or "")
        password = unquote(parsed.password or "")

        validate_connection_target(hostname, port)

        log.info(f"[MySQLAdapter] Ephemeral query to {hostname}:{port}/{database} -> table '{clean_table}'")
        con = None
        try:
            con = pymysql.connect(
                host=hostname,
                port=port,
                user=user,
                password=password,
                database=database,
                connect_timeout=5,
                read_timeout=10,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.Cursor
            )
            with con.cursor() as cursor:
                cursor.execute(f"SELECT * FROM `{clean_table}` LIMIT %s", (int(limit),))
                rows = [list(r) for r in cursor.fetchall()]
                columns = [col[0] for col in cursor.description] if cursor.description else []
                return columns, rows
        finally:
            if con:
                try:
                    con.close()
                except Exception:
                    pass


# ── MongoDB Adapter (pymongo - Pure Python Client) ─────────────────────────────
class MongoAdapter(ILiveDatabaseAdapter):
    """Extracts document collections from MongoDB into flattened tabular rows."""

    def fetch_data(self, uri: str, target: str, limit: int = 5000) -> Tuple[List[str], List[List[Any]]]:
        try:
            import pymongo
        except ImportError:
            raise RuntimeError("pymongo driver is required for MongoDB. Run: pip install pymongo")

        clean_collection = re.sub(r'[^a-zA-Z0-9_]', '', target.strip())
        if not clean_collection:
            raise ValueError("Invalid or empty target collection name.")

        parsed = urlparse(uri)
        hostname = parsed.hostname or ""
        if hostname:
            validate_connection_target(hostname, parsed.port)

        log.info(f"[MongoAdapter] Ephemeral extraction from collection '{clean_collection}'")
        client = None
        try:
            client = pymongo.MongoClient(
                uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=10000
            )
            db_name = parsed.path.lstrip("/").split("?")[0]
            if not db_name:
                db_names = client.list_database_names()
                user_dbs = [d for d in db_names if d not in ("admin", "config", "local")]
                db_name = user_dbs[0] if user_dbs else "admin"

            db = client[db_name]
            coll = db[clean_collection]

            docs = list(coll.find().limit(int(limit)))
            if not docs:
                return ["_id"], []

            headers_dict = {}
            for doc in docs:
                for k in doc.keys():
                    headers_dict[k] = True
            headers = list(headers_dict.keys())

            rows = []
            for doc in docs:
                row = []
                for h in headers:
                    val = doc.get(h)
                    if isinstance(val, (dict, list)):
                        import json
                        row.append(json.dumps(val, default=str))
                    elif hasattr(val, "__str__") and type(val).__name__ in ("ObjectId", "datetime"):
                        row.append(str(val))
                    else:
                        row.append(val)
                rows.append(row)

            return headers, rows
        finally:
            if client:
                try:
                    client.close()
                except Exception:
                    pass


# ── SQLite Adapter (Local Files) ───────────────────────────────────────────────
class SQLiteAdapter(ILiveDatabaseAdapter):
    """Extracts tables from a local or attached SQLite database file."""

    def fetch_data(self, uri: str, target: str, limit: int = 5000) -> Tuple[List[str], List[List[Any]]]:
        import sqlite3

        clean_table = re.sub(r'[^a-zA-Z0-9_]', '', target.strip())
        if not clean_table:
            raise ValueError("Invalid or empty target table name.")

        path = uri.replace("sqlite:///", "").replace("sqlite://", "")
        con = sqlite3.connect(path)
        try:
            cur = con.cursor()
            cur.execute(f'SELECT * FROM "{clean_table}" LIMIT ?', (int(limit),))
            columns = [d[0] for d in cur.description] if cur.description else []
            rows = [list(r) for r in cur.fetchall()]
            return columns, rows
        finally:
            con.close()


# ── Adapter Registry & Factory (OCP + SRP) ────────────────────────────────────
class DatabaseAdapterFactory:
    """Factory to resolve appropriate database adapter dynamically."""

    _adapters: Dict[str, ILiveDatabaseAdapter] = {
        "postgresql": PostgresAdapter(),
        "postgres": PostgresAdapter(),
        "pgsql": PostgresAdapter(),
        "mysql": MySQLAdapter(),
        "mariadb": MySQLAdapter(),
        "mongodb": MongoAdapter(),
        "mongo": MongoAdapter(),
        "sqlite": SQLiteAdapter(),
        "sqlite3": SQLiteAdapter(),
    }

    @classmethod
    def get_adapter(cls, db_type: str) -> ILiveDatabaseAdapter:
        key = db_type.strip().lower()
        adapter = cls._adapters.get(key)
        if not adapter:
            supported = ", ".join(sorted(set(cls._adapters.keys())))
            raise ValueError(f"Unsupported database engine '{db_type}'. Supported: {supported}")
        return adapter

    @classmethod
    def register_adapter(cls, name: str, adapter: ILiveDatabaseAdapter) -> None:
        """Allows runtime extension with custom adapters (OCP)."""
        cls._adapters[name.lower()] = adapter
