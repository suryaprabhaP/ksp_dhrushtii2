"""
KSP Sentinel AI — Cryptographic Audit Logger (Sec 65B Indian Evidence Act Compliance)
SOLID: SRP (Auditing Cryptography) + DIP (Pluggable IAuditRepository)
"""
import hashlib
import json
import logging
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

log = logging.getLogger("standalone.audit")


class AuditLogger:
    """
    Append-only causal chain audit logger.
    Emits structured SHA-256 hash-chained logs to Zoho Catalyst Cloud NoSQL Data Store
    and AppSail logs for Section 65B Indian Evidence Act admissibility certification.
    """
    def __init__(self, log_path: Path, audit_repo: Optional[Any] = None):
        self.log_path = Path(log_path)
        self.audit_repo = audit_repo
        self.last_hash = "GENESIS_BLOCK_00000000000000000000000000000000000000000000000000000000"
        self._lock = threading.Lock()
        self._init_chain()

    def _init_chain(self):
        # 1. Cloud-native: Rehydrate latest tail hash from Cloud NoSQL Audit Repository
        if self.audit_repo:
            try:
                cloud_hash = self.audit_repo.get_latest_hash()
                if cloud_hash:
                    self.last_hash = cloud_hash
                    log.info(f"[AuditLogger] Successfully rehydrated genesis hash from Cloud NoSQL: {self.last_hash}")
                    return
            except Exception as e:
                log.warning(f"[AuditLogger] Cloud genesis hash retrieval fallback: {e}")

        # 2. Local fallback: reconstruct from disk if file exists
        if self.log_path.exists():
            try:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            data = json.loads(line)
                            if "current_hash" in data:
                                self.last_hash = data["current_hash"]
            except Exception as e:
                log.warning(f"[AuditLogger] Failed to reconstruct genesis hash from file: {e}")

    def log_event(self, event_type: str, session_id: str, officer_id: str, action: str, details: Dict[str, Any] = None) -> str:
        ts = time.time()
        payload = {
            "timestamp": ts,
            "event_type": event_type,
            "session_id": session_id,
            "officer_id": officer_id,
            "action": action,
            "details": details or {},
            "prev_hash": self.last_hash
        }
        raw_str = json.dumps(payload, sort_keys=True)
        curr_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
        payload["current_hash"] = curr_hash
        self.last_hash = curr_hash

        with self._lock:
            # 1. Cloud-native stdout emission (captured by AppSail Cloud Logs)
            log.info(f"[AUDIT_RECORD] {json.dumps(payload)}")

            # 2. Persist to Cloud NoSQL Audit Repository (SOLID: DIP)
            if self.audit_repo:
                try:
                    self.audit_repo.append_log(payload)
                except Exception as e:
                    log.error(f"[AuditLogger] Failed to persist audit record to cloud repo: {e}")

            # 3. Local-only write (guarded against read-only environments)
            try:
                self.log_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(payload) + "\n")
            except OSError:
                # Graceful degradation in read-only container environments (AppSail)
                pass
            except Exception as e:
                log.error(f"[AuditLogger] Local file write notice: {e}")

        return curr_hash
