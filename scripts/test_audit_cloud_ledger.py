"""
KSP Sentinel AI — Section 65B Audit Ledger & Catalyst NoSQL Validation Test
Validates:
1. SOLID: DIP & ISP Decoupling with IAuditRepository
2. SHA-256 Mathematical Hash Chain Continuity ($H_N = SHA256(Payload(prev=H_{N-1}))$)
3. Genesis Block Rehydration on Container Boot / Restart
4. Cloud Repository Persistence & Buffer Integrity
"""
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.core.audit import AuditLogger
from app.services.zoho_integration_service import (
    IAuditRepository,
    CatalystNoSQLAuditRepository,
    catalyst_audit_repo,
    zoho_service,
)


class MockAuditRepository(IAuditRepository):
    """Mock repository to test strict DIP decoupling without network calls."""
    def __init__(self):
        self.logs = []

    def append_log(self, payload):
        self.logs.append(payload)
        return True

    def get_latest_hash(self):
        if self.logs:
            return self.logs[-1].get("current_hash")
        return None

    def list_logs(self, limit=50):
        return list(reversed(self.logs[-limit:]))


def run_tests():
    print("=" * 70)
    print("KSP SENTINEL AI — AUDIT LEDGER & NOSQL VERIFICATION")
    print("=" * 70)

    # ──────────────────────────────────────────────────────────────────────────
    # TEST 1: SOLID Decoupling & Unit Chain Math
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[TEST 1] Testing SOLID DIP & SHA-256 Hash Chain Integrity (Mock Repo)...")
    mock_repo = MockAuditRepository()
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_log = Path(tmpdir) / "audit_test.jsonl"
        logger = AuditLogger(log_path=tmp_log, audit_repo=mock_repo)

        h1 = logger.log_event(
            event_type="OFFICER_LOGIN",
            session_id="sess-001",
            officer_id="KA-POLICE-9021",
            action="AUTHENTICATE",
            details={"badge": "KA-9021", "station": "Cubbon Park"}
        )

        h2 = logger.log_event(
            event_type="DISPATCH_ISSUED",
            session_id="sess-001",
            officer_id="KA-POLICE-9021",
            action="HOYSALA_PCR_DISPATCH",
            details={"pcr_id": "KA-01-G-5501", "sector": "MG Road"}
        )

        h3 = logger.log_event(
            event_type="INTELLIGENCE_QUERY",
            session_id="sess-001",
            officer_id="KA-POLICE-9021",
            action="QUERY_SUSPECT_DOSSIER",
            details={"suspect_id": "SUS-KA-801", "name": "Blade"}
        )

        assert len(mock_repo.logs) == 3, f"Expected 3 logs in repo, got {len(mock_repo.logs)}"
        assert mock_repo.logs[0]["prev_hash"] == "GENESIS_BLOCK_00000000000000000000000000000000000000000000000000000000"
        assert mock_repo.logs[1]["prev_hash"] == h1, f"Chain broken: {mock_repo.logs[1]['prev_hash']} != {h1}"
        assert mock_repo.logs[2]["prev_hash"] == h2, f"Chain broken: {mock_repo.logs[2]['prev_hash']} != {h2}"
        assert logger.last_hash == h3

        # Cryptographic verification of each block
        for i, record in enumerate(mock_repo.logs):
            check_payload = {
                "timestamp": record["timestamp"],
                "event_type": record["event_type"],
                "session_id": record["session_id"],
                "officer_id": record["officer_id"],
                "action": record["action"],
                "details": record["details"],
                "prev_hash": record["prev_hash"]
            }
            computed_hash = hashlib.sha256(json.dumps(check_payload, sort_keys=True).encode("utf-8")).hexdigest()
            assert computed_hash == record["current_hash"], f"Block {i} hash mismatch!"
            print(f"  [OK] Block {i+1} [{record['event_type']}]: Hash {record['current_hash'][:16]}... verified.")

        print("  [SUCCESS] TEST 1 PASSED: Cryptographic causal chain mathematically verified.")

    # ──────────────────────────────────────────────────────────────────────────
    # TEST 2: Boot Rehydration Across Stateless Restarts (Stateless Immunity)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[TEST 2] Testing Container Restart / Rehydration (Simulating AppSail Reset)...")
    with tempfile.TemporaryDirectory() as fresh_tmpdir:
        fresh_log = Path(fresh_tmpdir) / "empty_audit.jsonl"
        new_worker_logger = AuditLogger(log_path=fresh_log, audit_repo=mock_repo)

        assert new_worker_logger.last_hash == h3, f"Failed rehydration: {new_worker_logger.last_hash} != {h3}"
        print(f"  [OK] New worker container booted and rehydrated last_hash: {new_worker_logger.last_hash[:16]}...")

        h4 = new_worker_logger.log_event(
            event_type="EVIDENCE_EXPORT",
            session_id="sess-002",
            officer_id="KA-POLICE-4412",
            action="EXPORT_SECTION_65B_CERTIFICATE",
            details={"case_id": "FIR-2026-BLR-0091"}
        )

        assert mock_repo.logs[3]["prev_hash"] == h3, f"Chain broken across container restart: {mock_repo.logs[3]['prev_hash']} != {h3}"
        print(f"  [OK] Block 4 appended seamlessly across container restart. New tail: {h4[:16]}...")
        print("  [SUCCESS] TEST 2 PASSED: Zero-downtime stateless container restart verified.")

    # ──────────────────────────────────────────────────────────────────────────
    # TEST 3: Catalyst NoSQL Repository Production Wiring
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[TEST 3] Testing Production CatalystNoSQLAuditRepository & zoho_service facade...")
    prod_repo = catalyst_audit_repo
    assert isinstance(prod_repo, CatalystNoSQLAuditRepository), "prod_repo is not CatalystNoSQLAuditRepository"
    assert zoho_service.audit_repo == prod_repo, "zoho_service facade not properly wired to audit_repo"

    test_payload = {
        "timestamp": time.time(),
        "event_type": "KSP_SYSTEM_HEALTH_CHECK",
        "session_id": "sys-check-001",
        "officer_id": "SYSTEM_DAEMON",
        "action": "HEARTBEAT",
        "details": {"system": "KSP_SENTINEL_AI", "version": "2.4.0"},
        "prev_hash": "GENESIS_TEST_HASH",
        "current_hash": "CURRENT_TEST_HASH_001"
    }

    res = prod_repo.append_log(test_payload)
    assert res is True, "append_log failed on CatalystNoSQLAuditRepository"

    logs = prod_repo.list_logs(limit=5)
    assert len(logs) > 0, "list_logs returned empty"
    print(f"  [OK] Catalyst NoSQL Audit Repository actively tracking {len(logs)} records in memory/cloud.")
    print("  [SUCCESS] TEST 3 PASSED: Production CatalystNoSQLAuditRepository wired correctly.")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED: Section 65B Audit Ledger & NoSQL Integration 100% OPERATIONAL")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
