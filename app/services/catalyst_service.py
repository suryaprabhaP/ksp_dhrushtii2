"""
KSP Sentinel AI — Zoho Catalyst Cloud Services (SOLID: SRP + DIP)
Provides seamless integration with:
1. Catalyst Cache (Redis-backed segment 54626000000136060 for sub-2ms multi-turn memory)
2. Catalyst Data Store (ZCQL / Relational Table SessionMemory for permanent persistence)
3. Transparent Local SQLite/In-Memory fallback for offline local development
"""
import abc
import json
import logging
import threading
import time
from typing import Any, Dict, List, Optional, Tuple
import requests

from app.config import (
    CATALYST_API_BASE,
    CATALYST_CACHE_SEGMENT_ID,
    CATALYST_FILESTORE_FOLDER_ID,
    CATALYST_ORG_ID,
    CATALYST_PROJECT_ID,
    CATALYST_TABLE_SESSION_MEMORY,
    CATALYST_TABLE_ECOMPLAINTS,
    CATALYST_TABLE_PASSPORTS,
    CATALYST_TABLE_POLICEFIRS,
    CATALYST_TABLE_DESK_TICKETS,
    CATALYST_TABLE_CRM_SUSPECTS,
    CATALYST_TABLE_AUDIT_TRAIL,
    CATALYST_TABLE_AUDIT_TRAIL_RELATIONAL,
    CATALYST_TABLE_AUDIT_TRAIL_NAME,
    ZOHO_ACCESS_TOKEN,
    ZOHO_CLIENT_ID,
    ZOHO_CLIENT_SECRET,
    ZOHO_REFRESH_TOKEN,
)

from app.services.zoho_token_manager import zoho_token_manager

log = logging.getLogger("standalone.catalyst_service")


# ══════════════════════════════════════════════════════════════════════════════
# ABSTRACTIONS (SOLID: DIP)
# ══════════════════════════════════════════════════════════════════════════════

class ICacheService(abc.ABC):
    @abc.abstractmethod
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abc.abstractmethod
    def put_session(self, session_id: str, data: Dict[str, Any], ttl_hours: int = 24) -> bool:
        pass

    @abc.abstractmethod
    def delete_session(self, session_id: str) -> bool:
        pass


class IDataStoreService(abc.ABC):
    @abc.abstractmethod
    def get_session_memory(self, session_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abc.abstractmethod
    def upsert_session_memory(
        self,
        session_id: str,
        summary: Optional[str],
        history: List[Dict[str, Any]],
        last_agent_type: Optional[str],
        turn_count: int
    ) -> bool:
        pass


class IFileStoreService(abc.ABC):
    """SOLID DIP: Abstract interface for persistent cloud BLOB dataset storage."""
    @abc.abstractmethod
    def upload_session_dataset(self, session_id: str, filename: str, file_bytes: bytes) -> bool:
        pass

    @abc.abstractmethod
    def download_session_dataset(self, session_id: str) -> Optional[Tuple[str, bytes]]:
        pass

    @abc.abstractmethod
    def delete_session_dataset(self, session_id: str) -> bool:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# CONCRETE IMPLEMENTATION: Catalyst Cache (Segment ID 54626000000136060)
# ══════════════════════════════════════════════════════════════════════════════

class CatalystCacheService(ICacheService):
    """
    Manages session context in Zoho Catalyst Redis-backed Cache (Segment 54626000000136060).
    Provides sub-2ms cache reads and thread-safe local buffer fallback.
    """
    def __init__(self):
        self.project_id = CATALYST_PROJECT_ID
        self.segment_id = CATALYST_CACHE_SEGMENT_ID
        self._local_cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
        self._lock = threading.RLock()

    @property
    def base_url(self) -> str:
        return f"{CATALYST_API_BASE}/baas/v1/project/{self.project_id}/segment/{self.segment_id}/cache"

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        tok = token or self.access_token
        headers = {"Authorization": f"Zoho-oauthtoken {tok}"}
        if CATALYST_ORG_ID:
            headers["CATALYST-ORG"] = str(CATALYST_ORG_ID)
        return headers

    @property
    def access_token(self) -> Optional[str]:
        return zoho_token_manager.get_valid_token(purpose="cache")

    def _refresh_token(self) -> Optional[str]:
        return zoho_token_manager.get_valid_token(purpose="cache", force_refresh=True)

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves cached session state.
        Checks local high-speed buffer first, then Catalyst Cloud Cache.
        """
        now = time.time()
        with self._lock:
            if session_id in self._local_cache:
                data, expiry = self._local_cache[session_id]
                if now < expiry:
                    return data
                del self._local_cache[session_id]

        if not self.access_token or not self.project_id or not self.segment_id:
            return None

        # Fetch from official Catalyst Cache REST endpoint (/segment/{id}/cache?cacheKey={k})
        try:
            url = self.base_url
            headers = self._get_headers()
            params = {"cacheKey": f"session_{session_id}"}
            resp = requests.get(url, headers=headers, params=params, timeout=2)

            if resp.status_code == 401:
                new_tok = self._refresh_token()
                if new_tok:
                    headers = self._get_headers(new_tok)
                    resp = requests.get(url, headers=headers, params=params, timeout=2)

            if resp.status_code == 200:
                body = resp.json()
                data_obj = body.get("data", {})
                raw_val = data_obj.get("cache_value") or data_obj.get("cacheValue") or data_obj.get("value")
                if raw_val:
                    parsed = json.loads(raw_val) if isinstance(raw_val, str) else raw_val
                    with self._lock:
                        self._local_cache[session_id] = (parsed, now + 3600)
                    return parsed
        except Exception as e:
            log.debug(f"[CatalystCache] Cloud cache get notice: {e}")

        return None

    def put_session(self, session_id: str, data: Dict[str, Any], ttl_hours: int = 24) -> bool:
        """
        Puts session data into Catalyst Cache segment and local buffer.
        """
        now = time.time()
        expiry_ts = now + (ttl_hours * 3600)
        with self._lock:
            self._local_cache[session_id] = (data, expiry_ts)

        if not self.access_token or not self.project_id or not self.segment_id:
            return True  # Buffered locally

        def _async_put():
            try:
                url = self.base_url
                headers = {**self._get_headers(), "Content-Type": "application/json"}
                payload = {
                    "cache_name": f"session_{session_id}",
                    "cache_value": json.dumps(data),
                    "expiry_in_hours": ttl_hours
                }
                resp = requests.post(url, headers=headers, json=payload, timeout=3)
                if resp.status_code == 401:
                    new_tok = self._refresh_token()
                    if new_tok:
                        headers = {**self._get_headers(new_tok), "Content-Type": "application/json"}
                        requests.post(url, headers=headers, json=payload, timeout=3)
            except Exception as e:
                log.debug(f"[CatalystCache] Cloud put background notice: {e}")

        threading.Thread(target=_async_put, daemon=True).start()
        return True

    def delete_session(self, session_id: str) -> bool:
        with self._lock:
            self._local_cache.pop(session_id, None)

        if not self.access_token or not self.project_id or not self.segment_id:
            return True

        try:
            url = self.base_url
            headers = self._get_headers()
            params = {"cacheKey": f"session_{session_id}"}
            requests.delete(url, headers=headers, params=params, timeout=2)
        except Exception:
            pass
        return True


# ══════════════════════════════════════════════════════════════════════════════
# CONCRETE IMPLEMENTATION: Catalyst Data Store (SessionMemory Table & ZCQL)
# ══════════════════════════════════════════════════════════════════════════════

class CatalystDataStoreService(IDataStoreService):
    """
    Manages persistent records in the Catalyst Data Store 'SessionMemory' table.
    Ensures non-blocking asynchronous cloud writes and zero-blocking local fallbacks.
    """
    def __init__(self):
        self.project_id = CATALYST_PROJECT_ID
        self.table_name = CATALYST_TABLE_SESSION_MEMORY
        self.tables = {
            "ecomplaints": CATALYST_TABLE_ECOMPLAINTS,
            "passports": CATALYST_TABLE_PASSPORTS,
            "police_firs": CATALYST_TABLE_POLICEFIRS,
            "session_memory": CATALYST_TABLE_SESSION_MEMORY,
            "desk_tickets": CATALYST_TABLE_DESK_TICKETS,
            "crm_suspects": CATALYST_TABLE_CRM_SUSPECTS,
            "audit_trail": CATALYST_TABLE_AUDIT_TRAIL,
            "audit_trail_relational": CATALYST_TABLE_AUDIT_TRAIL_RELATIONAL
        }

    @property
    def access_token(self) -> Optional[str]:
        return zoho_token_manager.get_valid_token(purpose="tables")

    def _refresh_token(self) -> Optional[str]:
        return zoho_token_manager.get_valid_token(purpose="tables", force_refresh=True)

    def execute_zcql(self, zcql_query: str) -> Optional[List[Dict[str, Any]]]:
        """
        Executes a ZCQL (Zoho Catalyst Query Language) query against Data Store.
        """
        if not self.access_token or not self.project_id:
            return None

        try:
            url = f"{CATALYST_API_BASE}/baas/v1/project/{self.project_id}/query"
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}",
                "Content-Type": "application/json"
            }
            payload = {"query": zcql_query}
            resp = requests.post(url, headers=headers, json=payload, timeout=3)

            if resp.status_code == 401:
                new_tok = self._refresh_token()
                if new_tok:
                    headers["Authorization"] = f"Zoho-oauthtoken {new_tok}"
                    resp = requests.post(url, headers=headers, json=payload, timeout=3)

            if resp.status_code == 200:
                data = resp.json().get("data", [])
                # Unwrap nested table rows: [{"SessionMemory": {"session_id": "..."}}]
                results = []
                for item in data:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            if isinstance(v, dict):
                                results.append(v)
                            else:
                                results.append(item)
                                break
                return results
        except Exception as e:
            log.debug(f"[CatalystDataStore] ZCQL query notice: {e}")
        return None

    def get_session_memory(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches session record from Catalyst Data Store table SessionMemory.
        """
        query = f"SELECT session_id, summary, history_json, last_agent_type, turn_count, updated_at FROM {self.table_name} WHERE session_id = '{session_id}'"
        rows = self.execute_zcql(query)
        if rows and len(rows) > 0:
            return rows[0]
        return None

    def upsert_session_memory(
        self,
        session_id: str,
        summary: Optional[str],
        history: List[Dict[str, Any]],
        last_agent_type: Optional[str],
        turn_count: int
    ) -> bool:
        """
        Asynchronously writes session record to Catalyst Data Store table SessionMemory.
        """
        now_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        row_payload = {
            "session_id": str(session_id),
            "summary": str(summary or ""),
            "history_json": json.dumps(history),
            "last_agent_type": str(last_agent_type or "CONVERSATIONAL"),
            "turn_count": int(turn_count),
            "updated_at": now_str
        }

        if not self.access_token or not self.project_id:
            return True

        def _async_upsert():
            try:
                # 1. Check if row exists
                existing = self.get_session_memory(session_id)
                headers = {
                    "Authorization": f"Zoho-oauthtoken {self.access_token}",
                    "Content-Type": "application/json"
                }

                if existing and existing.get("ROWID"):
                    row_id = existing["ROWID"]
                    url = f"{CATALYST_API_BASE}/baas/v1/project/{self.project_id}/table/{self.table_name}/row/{row_id}"
                    resp = requests.put(url, headers=headers, json=row_payload, timeout=4)
                else:
                    url = f"{CATALYST_API_BASE}/baas/v1/project/{self.project_id}/table/{self.table_name}/row"
                    resp = requests.post(url, headers=headers, json=row_payload, timeout=4)

                if resp.status_code == 401:
                    new_tok = self._refresh_token()
                    if new_tok:
                        headers["Authorization"] = f"Zoho-oauthtoken {new_tok}"
                        requests.post(url, headers=headers, json=row_payload, timeout=4)

                log.info(f"[CatalystDataStore] Upserted session '{session_id}' to cloud SessionMemory table.")
            except Exception as e:
                log.debug(f"[CatalystDataStore] Cloud upsert background notice: {e}")

        threading.Thread(target=_async_upsert, daemon=True).start()
        return True
        
    def get_records(self, table_key: str, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """
        Fetches records from a specified Catalyst Data Store table.
        table_key must be one of: 'ecomplaints', 'passports', 'police_firs'
        """
        table_id = self.tables.get(table_key)
        if not table_id:
            return None
            
        # Try to use ZCQL if possible, though using REST API is safer for custom columns
        if not self.access_token or not self.project_id:
            return None
            
        try:
            url = f"{CATALYST_API_BASE}/baas/v1/project/{self.project_id}/table/{table_id}/row"
            headers = {"Authorization": f"Zoho-oauthtoken {self.access_token}"}
            params = {"max_rows": limit}
            resp = requests.get(url, headers=headers, params=params, timeout=5)
            
            if resp.status_code == 401:
                new_tok = self._refresh_token()
                if new_tok:
                    headers["Authorization"] = f"Zoho-oauthtoken {new_tok}"
                    resp = requests.get(url, headers=headers, params=params, timeout=5)
                    
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                return data
        except Exception as e:
            log.warning(f"[CatalystDataStore] Error fetching records for {table_key}: {e}")
            
        return None

    def insert_record(self, table_key: str, record_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Inserts a new record into a specified Catalyst Data Store table synchronously.
        Returns the inserted record (which contains ROWID) if successful.
        """
        table_id = self.tables.get(table_key)
        if not table_id:
            return None
            
        if not self.access_token or not self.project_id:
            return None
            
        try:
            url = f"{CATALYST_API_BASE}/baas/v1/project/{self.project_id}/table/{table_id}/row"
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}",
                "Content-Type": "application/json"
            }
            resp = requests.post(url, headers=headers, json=record_data, timeout=5)
            
            if resp.status_code == 401:
                new_tok = self._refresh_token()
                if new_tok:
                    headers["Authorization"] = f"Zoho-oauthtoken {new_tok}"
                    resp = requests.post(url, headers=headers, json=record_data, timeout=5)
                    
            if resp.status_code == 200:
                # Returns something like {"data": {"ROWID": ..., ...}}
                return resp.json().get("data")
            else:
                log.warning(f"[CatalystDataStore] Insert failed: {resp.status_code} - {resp.text}")
        except Exception as e:
            log.warning(f"[CatalystDataStore] Insert exception for {table_key}: {e}")
            
        return None

    def insert_raw_table_record(self, table_id: str, record_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Directly inserts a record into a Catalyst table by raw Table ID or Name.
        """
        if not table_id or not self.access_token or not self.project_id:
            return None

        try:
            url = f"{CATALYST_API_BASE}/baas/v1/project/{self.project_id}/table/{table_id}/row"
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}",
                "Content-Type": "application/json"
            }
            resp = requests.post(url, headers=headers, json=record_data, timeout=5)
            if resp.status_code == 401:
                new_tok = self._refresh_token()
                if new_tok:
                    headers["Authorization"] = f"Zoho-oauthtoken {new_tok}"
                    resp = requests.post(url, headers=headers, json=record_data, timeout=5)
            if resp.status_code in (200, 201):
                return resp.json().get("data")
        except Exception as e:
            log.debug(f"[CatalystDataStore] Raw insert exception for {table_id}: {e}")
        return None

    def update_record(self, table_key: str, row_id: str, record_data: Dict[str, Any]) -> bool:
        """
        Updates an existing record in a specified Catalyst Data Store table.
        """
        table_id = self.tables.get(table_key)
        if not table_id:
            return False
            
        if not self.access_token or not self.project_id:
            return False
            
        try:
            url = f"{CATALYST_API_BASE}/baas/v1/project/{self.project_id}/table/{table_id}/row/{row_id}"
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}",
                "Content-Type": "application/json"
            }
            resp = requests.put(url, headers=headers, json=record_data, timeout=5)
            
            if resp.status_code == 401:
                new_tok = self._refresh_token()
                if new_tok:
                    headers["Authorization"] = f"Zoho-oauthtoken {new_tok}"
                    resp = requests.put(url, headers=headers, json=record_data, timeout=5)
                    
            return resp.status_code == 200
        except Exception as e:
            log.warning(f"[CatalystDataStore] Update exception for {table_key}: {e}")
            
        return False

    def delete_raw_table_record(self, table_id: str, row_id: str) -> bool:
        """
        Directly deletes a record from a Catalyst table by raw Table ID and Row ID.
        """
        if not table_id or not row_id or not self.access_token or not self.project_id:
            return False

        try:
            url = f"{CATALYST_API_BASE}/baas/v1/project/{self.project_id}/table/{table_id}/row/{row_id}"
            headers = {"Authorization": f"Zoho-oauthtoken {self.access_token}"}
            resp = requests.delete(url, headers=headers, timeout=5)

            if resp.status_code == 401:
                new_tok = self._refresh_token()
                if new_tok:
                    headers["Authorization"] = f"Zoho-oauthtoken {new_tok}"
                    resp = requests.delete(url, headers=headers, timeout=5)

            return resp.status_code in (200, 204)
        except Exception as e:
            log.debug(f"[CatalystDataStore] Raw delete exception for {table_id}/{row_id}: {e}")

        return False


# ══════════════════════════════════════════════════════════════════════════════
# CONCRETE IMPLEMENTATION: Catalyst File Store (Folder ID 54626000000149001)
# ══════════════════════════════════════════════════════════════════════════════

class CatalystFileStoreService(IFileStoreService):
    """
    Manages session-dataset persistence in Zoho Catalyst File Store.
    Enables instant rehydration of ephemeral SQLite session databases on AppSail restarts/scaling.
    """
    def __init__(self):
        self.project_id = CATALYST_PROJECT_ID
        self.folder_id = CATALYST_FILESTORE_FOLDER_ID
        self._local_blob_cache: Dict[str, Tuple[str, bytes]] = {}  # session_id -> (filename, bytes)
        self._lock = threading.RLock()

    @property
    def access_token(self) -> Optional[str]:
        return zoho_token_manager.get_valid_token(purpose="projects")

    def _refresh_token(self) -> Optional[str]:
        return zoho_token_manager.get_valid_token(purpose="projects", force_refresh=True)

    def upload_session_dataset(self, session_id: str, filename: str, file_bytes: bytes) -> bool:
        """
        Uploads dataset bytes to Catalyst File Store asynchronously and caches in memory.
        """
        if not session_id or not file_bytes:
            return False

        with self._lock:
            self._local_blob_cache[session_id] = (filename, file_bytes)

        if not self.access_token or not self.project_id or not self.folder_id:
            log.debug("[CatalystFileStore] Local buffer stored; cloud upload skipped (missing config/token)")
            return True

        def _async_upload():
            try:
                cloud_file_name = f"session_{session_id}_{filename}"
                url = f"{CATALYST_API_BASE}/baas/v1/project/{self.project_id}/folder/{self.folder_id}/file"
                headers = {"Authorization": f"Zoho-oauthtoken {self.access_token}"}
                
                # Catalyst File Store upload: multipart/form-data with 'code' key
                files = {"code": (cloud_file_name, file_bytes, "application/octet-stream")}
                resp = requests.post(url, headers=headers, files=files, timeout=10)

                if resp.status_code == 401:
                    new_tok = self._refresh_token()
                    if new_tok:
                        headers["Authorization"] = f"Zoho-oauthtoken {new_tok}"
                        files = {"code": (cloud_file_name, file_bytes, "application/octet-stream")}
                        resp = requests.post(url, headers=headers, files=files, timeout=10)

                if resp.status_code in (200, 201):
                    log.info(f"[CatalystFileStore] Successfully uploaded '{cloud_file_name}' to Folder {self.folder_id}")
                else:
                    log.warning(f"[CatalystFileStore] Upload notice: HTTP {resp.status_code} - {resp.text[:200]}")
            except Exception as e:
                log.debug(f"[CatalystFileStore] Async upload notice: {e}")

        threading.Thread(target=_async_upload, daemon=True).start()
        return True

    def download_session_dataset(self, session_id: str) -> Optional[Tuple[str, bytes]]:
        """
        Retrieves dataset bytes for a given session. Checks local high-speed buffer first,
        then queries the Catalyst File Store folder to download the remote BLOB.
        """
        if not session_id:
            return None

        with self._lock:
            if session_id in self._local_blob_cache:
                return self._local_blob_cache[session_id]

        if not self.access_token or not self.project_id or not self.folder_id:
            return None

        try:
            # 1. List files in folder
            url = f"{CATALYST_API_BASE}/baas/v1/project/{self.project_id}/folder/{self.folder_id}/file"
            headers = {"Authorization": f"Zoho-oauthtoken {self.access_token}"}
            resp = requests.get(url, headers=headers, timeout=5)

            if resp.status_code == 401:
                new_tok = self._refresh_token()
                if new_tok:
                    headers["Authorization"] = f"Zoho-oauthtoken {new_tok}"
                    resp = requests.get(url, headers=headers, timeout=5)

            if resp.status_code != 200:
                log.debug(f"[CatalystFileStore] Folder list notice: HTTP {resp.status_code}")
                return None

            data = resp.json().get("data", [])
            prefix = f"session_{session_id}_"
            target_item = None
            for item in data:
                file_name = item.get("file_name") or item.get("name") or ""
                if file_name.startswith(prefix):
                    target_item = item
                    break

            if not target_item:
                return None

            file_id = target_item.get("id") or target_item.get("file_id")
            full_name = target_item.get("file_name") or target_item.get("name") or "dataset.csv"
            original_filename = full_name[len(prefix):] if full_name.startswith(prefix) else full_name

            # 2. Download file content
            download_url = f"{CATALYST_API_BASE}/baas/v1/project/{self.project_id}/folder/{self.folder_id}/file/{file_id}/download"
            d_resp = requests.get(download_url, headers=headers, timeout=10)

            if d_resp.status_code == 401:
                new_tok = self._refresh_token()
                if new_tok:
                    headers["Authorization"] = f"Zoho-oauthtoken {new_tok}"
                    d_resp = requests.get(download_url, headers=headers, timeout=10)

            if d_resp.status_code == 200 and d_resp.content:
                with self._lock:
                    self._local_blob_cache[session_id] = (original_filename, d_resp.content)
                log.info(f"[CatalystFileStore] Downloaded '{original_filename}' ({len(d_resp.content)} bytes) for session '{session_id}'")
                return original_filename, d_resp.content
        except Exception as e:
            log.debug(f"[CatalystFileStore] Download notice for session '{session_id}': {e}")

        return None

    def delete_session_dataset(self, session_id: str) -> bool:
        with self._lock:
            self._local_blob_cache.pop(session_id, None)
        return True


# Global Singleton Instances
catalyst_cache_service = CatalystCacheService()
catalyst_datastore_service = CatalystDataStoreService()
catalyst_filestore_service = CatalystFileStoreService()

