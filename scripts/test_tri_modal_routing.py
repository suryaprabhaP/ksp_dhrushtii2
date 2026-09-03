"""
Comprehensive Test Suite: Tri-Modal Dataset Routing & Domain Isolation
========================================================================
Validates:
1. Slot Overwrite: Uploading a new CSV in the same slot eradicates the previous table.
2. Cross-Slot Preservation: Ingesting into one slot does NOT eradicate other slots.
3. Memory Invariance: MemoryAgent session turns remain intact across uploads.
4. Schema Routing: get_table_for_query routes accurately by query domain intent.
5. SQL Execution: Standard ANSI SQL queries succeed on active slots.
"""
import sys
import os
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.engine.session_store import session_store
from app.core.memory import MemoryAgent

def run_tests():
    print("=" * 70)
    print("KSP SENTINEL AI — TRI-MODAL DATASET ROUTING TEST SUITE")
    print("=" * 70)
    
    session_id = "test_officer_session_99"
    
    # ── TEST 1: Initial Memory Seeding ──────────────────────────────────────────
    print("\n[TEST 1] Seeding Chat Conversational Memory...")
    MemoryAgent.save_session_turn(session_id, "user", "Officer logged in for Bengaluru Central duty.", agent_type="CONVERSATIONAL")
    MemoryAgent.save_session_turn(session_id, "assistant", "Acknowledged Officer. Ready for crime analysis.", agent_type="CONVERSATIONAL")
    
    history, summary, last_agent = MemoryAgent.get_session_history(session_id)
    assert len(history) >= 2, "Failed to seed history"
    print(f"  [PASS] Memory seeded: {len(history)} turns present in session.")

    # ── TEST 2: Ingest Crime Analytics Dataset (Slot 1) ───────────────────────
    print("\n[TEST 2] Ingesting Crime Analytics Dataset into 'analytics' slot...")
    csv_crime_v1 = b"fir_no,district,crime_type,ipc_section\nFIR-001,Bengaluru,Cyber Fraud,420\nFIR-002,Bengaluru,Robbery,392"
    res1 = session_store.ingest_dataset(
        session_id=session_id,
        filename="bengaluru_crimes_v1.csv",
        file_bytes=csv_crime_v1,
        upload_to_cloud=False,
        dataset_purpose="analytics"
    )
    assert res1["table_name"] == "crime_dataset", f"Expected 'crime_dataset', got {res1['table_name']}"
    assert res1["row_count"] == 2, f"Expected 2 rows, got {res1['row_count']}"
    assert res1["classification"] == "ANALYTICAL"
    print(f"  [PASS] Slot 1 created: table '{res1['table_name']}' ({res1['row_count']} rows, classification: {res1['classification']})")

    # ── TEST 3: Ingest Network Graph Dataset (Slot 2) ──────────────────────────
    print("\n[TEST 3] Ingesting Network Graph Dataset into 'network' slot...")
    csv_network = b"source,target,phone_number,transaction_amount\nSuspectA,Mule1,9876543210,50000\nSuspectB,Mule2,9876543211,75000"
    res2 = session_store.ingest_dataset(
        session_id=session_id,
        filename="mule_network.csv",
        file_bytes=csv_network,
        upload_to_cloud=False,
        dataset_purpose="network"
    )
    assert res2["table_name"] == "network_dataset", f"Expected 'network_dataset', got {res2['table_name']}"
    assert res2["row_count"] == 2
    assert res2["classification"] == "GRAPH"
    print(f"  [PASS] Slot 2 created: table '{res2['table_name']}' ({res2['row_count']} rows, classification: {res2['classification']})")

    # Verify BOTH slots exist simultaneously
    active_tables = list(session_store.sessions[session_id]["tables"].keys())
    assert "crime_dataset" in active_tables, "Slot 1 was prematurely dropped!"
    assert "network_dataset" in active_tables, "Slot 2 was not created!"
    print(f"  [PASS] Cross-Slot Coexistence Verified: Active tables = {active_tables}")

    # ── TEST 4: Ingest Geospatial Dataset (Slot 3) ─────────────────────────────
    print("\n[TEST 4] Ingesting Geospatial Dataset into 'spatial' slot...")
    csv_spatial = b"location_id,latitude,longitude,hotspot_name\nLOC-1,12.9716,77.5946,MG Road\nLOC-2,12.9352,77.6245,Koramangala"
    res3 = session_store.ingest_dataset(
        session_id=session_id,
        filename="bangalore_hotspots.csv",
        file_bytes=csv_spatial,
        upload_to_cloud=False,
        dataset_purpose="spatial"
    )
    assert res3["table_name"] == "spatial_dataset"
    assert res3["row_count"] == 2
    assert res3["classification"] == "SPATIAL"
    print(f"  [PASS] Slot 3 created: table '{res3['table_name']}' ({res3['row_count']} rows, classification: {res3['classification']})")

    # Verify ALL THREE slots exist
    active_tables = list(session_store.sessions[session_id]["tables"].keys())
    assert "crime_dataset" in active_tables
    assert "network_dataset" in active_tables
    assert "spatial_dataset" in active_tables
    print(f"  [PASS] Tri-Modal Triad Verified: Active tables = {active_tables}")

    # ── TEST 5: Slot Overwrite (Replace Crime Analytics without touching others)
    print("\n[TEST 5] Testing Slot Overwrite (Uploading new Crime Analytics v2)...")
    csv_crime_v2 = b"fir_no,district,crime_type,ipc_section,status\nFIR-101,Mysuru,Cyber Fraud,420,Pending\nFIR-102,Mysuru,Theft,379,Closed\nFIR-103,Mysuru,Extortion,384,Active"
    res4 = session_store.ingest_dataset(
        session_id=session_id,
        filename="mysuru_crimes_v2.csv",
        file_bytes=csv_crime_v2,
        upload_to_cloud=False,
        dataset_purpose="analytics"
    )
    assert res4["table_name"] == "crime_dataset"
    assert res4["row_count"] == 3

    # Query crime_dataset to verify old data (2 rows) is replaced by new data (3 rows)
    cols, rows = session_store.execute_sql(session_id, "SELECT * FROM crime_dataset")
    assert len(rows) == 3, f"Expected 3 rows in overwritten crime_dataset, got {len(rows)}"
    assert "status" in cols, "Expected new column 'status' in overwritten schema"
    print(f"  [PASS] Slot Overwrite Verified: 'crime_dataset' updated from 2 -> 3 rows with fresh schema ({cols}).")

    # Verify other slots were NOT affected
    cols_net, rows_net = session_store.execute_sql(session_id, "SELECT * FROM network_dataset")
    assert len(rows_net) == 2, "network_dataset was corrupted by analytics upload!"
    cols_spat, rows_spat = session_store.execute_sql(session_id, "SELECT * FROM spatial_dataset")
    assert len(rows_spat) == 2, "spatial_dataset was corrupted by analytics upload!"
    print("  [PASS] Domain Isolation Verified: 'network_dataset' and 'spatial_dataset' remain 100% intact.")

    # ── TEST 6: Conversational Memory Invariance ──────────────────────────────
    print("\n[TEST 6] Verifying Conversational Memory Invariance...")
    history_after, _, _ = MemoryAgent.get_session_history(session_id)
    assert len(history_after) >= 2, "Conversational memory was wiped during dataset upload!"
    assert any("Officer logged in" in turn.get("content", "") for turn in history_after)
    print(f"  [PASS] Memory Invariance Verified: All {len(history_after)} turns preserved intact.")

    # ── TEST 7: Query Intent Routing ──────────────────────────────────────────
    print("\n[TEST 7] Testing Dynamic Query Router (get_table_for_query)...")
    
    t_net = session_store.get_table_for_query(session_id, "Find all mule accounts and upi transactions for suspect")
    assert t_net == "network_dataset", f"Expected network_dataset, got {t_net}"
    print(f"  [PASS] Network query routed to: '{t_net}'")

    t_spat = session_store.get_table_for_query(session_id, "Show latitude and longitude coordinates on the hotspot map")
    assert t_spat == "spatial_dataset", f"Expected spatial_dataset, got {t_spat}"
    print(f"  [PASS] Geospatial query routed to: '{t_spat}'")

    t_crime = session_store.get_table_for_query(session_id, "Count total IPC 420 cases by district")
    assert t_crime == "crime_dataset", f"Expected crime_dataset, got {t_crime}"
    print(f"  [PASS] Analytical query routed to: '{t_crime}'")

    print("\n" + "=" * 70)
    print("ALL 7 TRI-MODAL ARCHITECTURAL TESTS PASSED SUCCESSFULLY! (100% GREEN)")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
