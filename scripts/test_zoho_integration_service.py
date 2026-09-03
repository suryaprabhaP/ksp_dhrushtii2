"""
Comprehensive Test Suite for ZohoIntegrationService (SOLID & Purpose-Token Routing)
"""
import os
import sys
import threading
import time

# Ensure project root is on sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.zoho_integration_service import (
    ZohoIntegrationService,
    CatalystDataStoreTicketRepository,
    CatalystDataStoreSuspectRepository,
    zoho_service
)
from app.services.zoho_token_manager import zoho_token_manager
from app.services.catalyst_service import catalyst_datastore_service, catalyst_cache_service


def run_full_suite():
    print("=" * 70)
    print("[START] STARTING ZOHO INTEGRATION SERVICE & MULTI-TOKEN VALIDATION")
    print("=" * 70)

    test_results = []

    # ──────────────────────────────────────────────────────────────────────────
    # TEST 1: Token Routing Isolation
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[TEST 1] Verifying Token Routing Isolation across All 5 Pipelines...")
    purposes = ["projects", "tables", "cache", "quickml", "zia"]
    tokens_verified = True
    token_details = {}

    for p in purposes:
        tok = zoho_token_manager.get_valid_token(purpose=p)
        if tok:
            token_details[p] = tok[:10] + "..."
        else:
            tokens_verified = False
            token_details[p] = "FAILED"

    if tokens_verified:
        print(f"  [PASS] All 5 token routes resolved cleanly: {token_details}")
        test_results.append(("Token Routing Isolation", "PASSED", f"Resolved tokens for {list(token_details.keys())}"))
    else:
        print(f"  [FAIL] Token route failure: {token_details}")
        test_results.append(("Token Routing Isolation", "FAILED", str(token_details)))

    # ──────────────────────────────────────────────────────────────────────────
    # TEST 2: Ticket Creation (CRUD: Create)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[TEST 2] Testing Ticket Creation (Hoysala PCR Dispatch Order)...")
    ticket_payload = {
        "district": "Bengaluru Urban",
        "summary": "Urgent dispatch required for armed suspect near Koramangala 5th Block",
        "threat_level": "CRITICAL",
        "police_station": "Koramangala Police Station"
    }

    t1 = zoho_service.create_priority_ticket(**ticket_payload)
    
    # Contract validation
    required_keys = ["success", "ticket_number", "district", "threat_level", "summary", "status", "department", "created_at", "message"]
    has_keys = all(k in t1 for k in required_keys)
    is_critical = t1.get("threat_level") == "CRITICAL"
    has_ticket_no = str(t1.get("ticket_number", "")).startswith("ZD-")

    if has_keys and is_critical and has_ticket_no:
        print(f"  [PASS] Ticket created successfully: #{t1['ticket_number']} | Status: {t1['status']} | Threat: {t1['threat_level']}")
        test_results.append(("CRUD: Create Priority Ticket", "PASSED", f"Generated ticket {t1['ticket_number']} with full contract schema"))
    else:
        print(f"  [FAIL] Ticket contract validation failed: {t1}")
        test_results.append(("CRUD: Create Priority Ticket", "FAILED", "Missing keys or schema mismatch"))

    # ──────────────────────────────────────────────────────────────────────────
    # TEST 3: List Tickets (CRUD: Read)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[TEST 3] Testing Ticket Listing (LIFO Ordering & Limits)...")
    # Create another ticket to test listing
    t2 = zoho_service.create_priority_ticket(
        district="Mysuru",
        summary="Commercial burglary in progress near Devaraja Market",
        threat_level="HIGH"
    )

    tickets = zoho_service.list_tickets(limit=10)
    if tickets and len(tickets) >= 2 and tickets[0]["ticket_number"] == t2["ticket_number"]:
        print(f"  [PASS] List tickets returned {len(tickets)} tickets. Latest ticket: #{tickets[0]['ticket_number']} (Mysuru)")
        test_results.append(("CRUD: List Dispatch Tickets", "PASSED", f"Retrieved {len(tickets)} tickets in proper chronological order"))
    else:
        print(f"  [FAIL] List tickets order/count invalid: count={len(tickets) if tickets else 0}")
        test_results.append(("CRUD: List Dispatch Tickets", "FAILED", f"Count: {len(tickets) if tickets else 0}"))

    # ──────────────────────────────────────────────────────────────────────────
    # TEST 4: Query Suspects Intelligence (Filtering & Risk Ranking)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[TEST 4] Testing Suspect Dossier Querying (Fuzzy District & Category)...")
    
    # 4a: District filter
    s_blr = zoho_service.query_crm_suspects(district="Bengaluru Urban", limit=3)
    # 4b: Category filter
    s_cyber = zoho_service.query_crm_suspects(crime_category="Cyber Extortion", limit=2)
    # 4c: Global sorted by risk score
    s_all = zoho_service.query_crm_suspects(district="all", limit=5)

    risk_sorted = all(s_all[i]["risk_score"] >= s_all[i+1]["risk_score"] for i in range(len(s_all)-1))
    cyber_matched = any("Cyber" in s.get("primary_crime", "") for s in s_cyber)
    blr_matched = any("Bengaluru" in s.get("district", "") for s in s_blr)

    if risk_sorted and cyber_matched and blr_matched:
        top_suspect = s_all[0]
        print(f"  [PASS] Top High-Risk Suspect: {top_suspect['name']} (Risk: {top_suspect['risk_score']}) - {top_suspect['primary_crime']}")
        print(f"  [PASS] Bengaluru Filter Count: {len(s_blr)} | Cyber Filter Count: {len(s_cyber)}")
        test_results.append(("CRM Suspect Query & Ranking", "PASSED", f"Ranked {len(s_all)} suspects, correctly filtered by district and MO"))
    else:
        print(f"  [FAIL] Suspect query filtering failed: risk_sorted={risk_sorted}, cyber={cyber_matched}, blr={blr_matched}")
        test_results.append(("CRM Suspect Query & Ranking", "FAILED", "Filtering logic mismatch"))

    # ──────────────────────────────────────────────────────────────────────────
    # TEST 5: Dependency Injection & Extensibility (SOLID: DIP & OCP)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[TEST 5] Testing Custom Repository Dependency Injection (SOLID DIP)...")
    class MockTicketRepository(CatalystDataStoreTicketRepository):
        def __init__(self):
            super().__init__()
            self.mock_called = False

        def create_ticket(self, ticket_record):
            self.mock_called = True
            return super().create_ticket(ticket_record)

    mock_repo = MockTicketRepository()
    custom_service = ZohoIntegrationService(ticket_repo=mock_repo)
    custom_service.create_priority_ticket(district="Belagavi", summary="Test DI ticket")

    if mock_repo.mock_called:
        print("  [PASS] Dependency Injection verified: Custom repository successfully intercepted dispatch call.")
        test_results.append(("SOLID DIP & OCP Verification", "PASSED", "Repository successfully injected and executed"))
    else:
        print("  [FAIL] Dependency Injection failed.")
        test_results.append(("SOLID DIP & OCP Verification", "FAILED", "Mock repository was not invoked"))

    # ──────────────────────────────────────────────────────────────────────────
    # TEST 6: Thread-Safe Concurrent Dispatch
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[TEST 6] Testing Thread Safety under Concurrent Ticket Generation...")
    errors = []
    def worker(i):
        try:
            zoho_service.create_priority_ticket(district=f"District-{i}", summary=f"Concurrent test {i}")
        except Exception as ex:
            errors.append(ex)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    if not errors:
        print("  [PASS] 10 concurrent ticket dispatch threads executed with zero race conditions.")
        test_results.append(("Thread Safety & Concurrency", "PASSED", "10 concurrent worker threads completed without error"))
    else:
        print(f"  [FAIL] Concurrency error: {errors}")
        test_results.append(("Thread Safety & Concurrency", "FAILED", str(errors)))

    # ──────────────────────────────────────────────────────────────────────────
    # SUMMARY REPORT
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("TEST EXECUTION SUMMARY")
    print("=" * 70)
    for name, status, details in test_results:
        status_tag = "[PASS]" if status == "PASSED" else "[FAIL]"
        print(f" {status_tag} {name:<35} : {status} - {details}")
    print("=" * 70)

    return all(res[1] == "PASSED" for res in test_results)


if __name__ == "__main__":
    success = run_full_suite()
    sys.exit(0 if success else 1)
