"""
Test Script: Catalyst File Store Stateless SQLite Rehydration
Validates:
1. Ingestion of CSV into session_store with cloud File Store sync
2. Simulated stateless container crash / scale-out (clearing session_store.sessions)
3. Transparent lazy rehydration of dataset and SQL execution on a fresh in-memory SQLite DB
"""
import sys
import os
import time

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import CATALYST_FILESTORE_FOLDER_ID, CATALYST_PROJECT_ID
from app.services.catalyst_service import catalyst_filestore_service
from app.engine.session_store import session_store

def run_test():
    print("=" * 80)
    print("TEST: Catalyst File Store Stateless SQLite Rehydration")
    print(f"Catalyst Project ID: {CATALYST_PROJECT_ID}")
    print(f"Catalyst FileStore Folder ID: {CATALYST_FILESTORE_FOLDER_ID}")
    print("=" * 80)

    test_session_id = f"test_session_{int(time.time())}"
    sample_csv = (
        "fir_number,crime_type,station,amount_lost,suspect_name\n"
        "FIR-2026-001,Cyber Fraud,Whitefield,54000,Ramesh\n"
        "FIR-2026-002,Robbery,Indiranagar,120000,Suresh\n"
        "FIR-2026-003,UPI Scam,Koramangala,35000,Dinesh\n"
    ).encode("utf-8")

    # Step 1: Initial Ingestion
    print(f"\n[Step 1] Ingesting CSV dataset into session '{test_session_id}'...")
    res = session_store.ingest_dataset(test_session_id, "crimes_sample.csv", sample_csv, upload_to_cloud=True)
    print(f"Ingestion result: {res}")
    assert res["success"] is True, "Ingestion failed"
    assert res["row_count"] == 3, "Row count mismatch"

    # Step 2: Query in current memory
    print(f"\n[Step 2] Executing SQL query in initial in-memory DB...")
    cols, rows = session_store.execute_sql(test_session_id, "SELECT crime_type, station, amount_lost FROM crime_dataset WHERE amount_lost > 40000")
    print(f"Columns: {cols}")
    print(f"Rows ({len(rows)}): {rows}")
    assert len(rows) == 2, f"Expected 2 rows, got {len(rows)}"

    # Allow async cloud upload thread to complete (or buffer locally)
    time.sleep(1.0)

    # Step 3: Simulate AppSail Container Crash / Stateless Reset
    print(f"\n[Step 3] [RESET] SIMULATING APPSAIL CONTAINER RESTART / SCALE-OUT")
    print("Wiping all local in-memory SQLite instances...")
    session_store.sessions.clear()
    assert test_session_id not in session_store.sessions, "Session was not cleared"
    print(f"Verified: session_store.sessions is now empty: {session_store.sessions}")

    # Step 4: Transparent Lazy Rehydration Trigger
    print(f"\n[Step 4] Querying dataset on stateless container (triggers rehydrate_session)...")
    has_data = session_store.has_dataset(test_session_id)
    print(f"has_dataset('{test_session_id}'): {has_data}")
    assert has_data is True, "has_dataset failed to rehydrate from File Store"

    # Step 5: Execute SQL on Rehydrated Database
    print(f"\n[Step 5] Executing SQL on restored in-memory SQLite database...")
    cols_rehydrated, rows_rehydrated = session_store.execute_sql(
        test_session_id,
        "SELECT suspect_name, crime_type, amount_lost FROM crime_dataset ORDER BY amount_lost DESC"
    )
    print(f"Columns: {cols_rehydrated}")
    print(f"Rows ({len(rows_rehydrated)}): {rows_rehydrated}")
    assert len(rows_rehydrated) == 3, f"Expected 3 rows in rehydrated database, got {len(rows_rehydrated)}"
    assert rows_rehydrated[0][0] == "Suresh", "Data ordering/integrity mismatch"

    # Step 6: Verify Schema Summary & Column Metadata
    summary = session_store.get_schema_summary(test_session_id)
    print(f"\n[Step 6] Restored Schema Summary: {summary}")
    assert "crime_dataset" in summary

    print("\n" + "=" * 80)
    print("[SUCCESS] ALL TESTS PASSED: Catalyst File Store Stateless Rehydration fully functional!")
    print("=" * 80)

if __name__ == "__main__":
    run_test()
