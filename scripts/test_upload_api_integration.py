"""
Integration Test: Flask /api/upload_dataset with dataset_purpose
================================================================
Validates end-to-end HTTP request processing with Flask test client.
"""
import io
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from server import app
from app.engine.session_store import session_store

def run_http_tests():
    print("=" * 70)
    print("KSP SENTINEL AI — HTTP INGESTION API INTEGRATION TEST")
    print("=" * 70)

    client = app.test_client()
    session_id = "http_test_officer_session_42"

    # 1. Upload Analytics Dataset via HTTP
    print("\n[HTTP TEST 1] POST /api/upload_dataset with purpose='analytics'...")
    data = {
        "file": (io.BytesIO(b"fir_id,crime_type,year\nFIR-01,Extortion,2025"), "cases.csv"),
        "session_id": session_id,
        "officer_id": "OFFICER_007",
        "dataset_purpose": "analytics"
    }
    resp = client.post("/api/upload_dataset", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200, f"Failed: {resp.data}"
    json_data = resp.get_json()
    assert json_data["success"] is True
    assert json_data["table_name"] == "crime_dataset"
    print(f"  [PASS] Uploaded as '{json_data['table_name']}', classification: '{json_data['classification']}'")

    # 2. Upload Network Dataset via HTTP
    print("\n[HTTP TEST 2] POST /api/upload_dataset with purpose='network'...")
    data_net = {
        "file": (io.BytesIO(b"source,target,calls\nA,B,10"), "cdr.csv"),
        "session_id": session_id,
        "officer_id": "OFFICER_007",
        "dataset_purpose": "network"
    }
    resp_net = client.post("/api/upload_dataset", data=data_net, content_type="multipart/form-data")
    assert resp_net.status_code == 200
    json_net = resp_net.get_json()
    assert json_net["table_name"] == "network_dataset"
    print(f"  [PASS] Uploaded as '{json_net['table_name']}', classification: '{json_net['classification']}'")

    # 3. Check Session Store Tables via API /api/datasets
    print("\n[HTTP TEST 3] GET /api/datasets...")
    resp_list = client.get(f"/api/datasets?session_id={session_id}")
    assert resp_list.status_code == 200
    json_list = resp_list.get_json()
    assert "crime_dataset" in json_list["tabular_tables"]
    assert "network_dataset" in json_list["tabular_tables"]
    print(f"  [PASS] Session tables verified via API: {json_list['tabular_tables']}")

    print("\n" + "=" * 70)
    print("ALL HTTP INTEGRATION TESTS PASSED SUCCESSFULLY! (100% GREEN)")
    print("=" * 70)

if __name__ == "__main__":
    run_http_tests()
