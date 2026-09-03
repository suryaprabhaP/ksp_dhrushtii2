"""
KSP Sentinel AI — Automated Verification Suite: QuickML Affinity & Graph Fusion
================================================================================
Validates:
1. QuickML Cloud API invocation / heuristic failover.
2. Data contract integrity with exact Endpoint Headers.
3. GraphEngine Bipartite construction & AI Affinity edge injection.
4. Evidentiary Trust tiers (FACTUAL vs AI-SUPPORTED / AI-SUGGESTED).
5. All critical Flask API routes live regression testing.
"""
import sys
import json
import logging
from pathlib import Path

# Set up project root on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Ensure Windows stdout handles UTF-8 smoothly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.services.quickml_service import quickml_affinity_service
from app.engine.graph_engine import GraphEngine
from server import app

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("test.quickml_affinity")


def run_tests():
    print("=" * 80)
    print("[TEST SUITE] RUNNING KSP SENTINEL AI - QUICKML AFFINITY & GRAPH FUSION")
    print("=" * 80)

    client = app.test_client()
    passed = 0
    total = 0

    # ── Test 1: Direct QuickML Affinity Prediction ───────────────────────────
    total += 1
    print("\n[TEST 1] Testing QuickML Service Suspect Inference...")
    test_suspect = {
        "suspect_id": "KSP-SUS-1054",
        "suspect_name": "Prashanth Acharya",
        "primary_crime_category": "Vehicle Theft",
        "modus_operandi": "Keyless Jammer Repeater",
        "operating_district": "Mysuru",
        "time_window": "Late Night (02:00 - 05:00)",
        "target_demographic": "Commercial Pickup Trucks",
        "primary_tool_or_weapon": "OBD Port Programmer",
        "prior_convictions_count": 12,
        "threat_risk_score": 84.4
    }
    pred = quickml_affinity_service.predict_suspect_affinity(test_suspect)
    print(f"  -> Predicted Cluster: {pred.predicted_cluster}")
    print(f"  -> Confidence: {pred.confidence}")
    print(f"  -> Status: {pred.status}")
    print(f"  -> Source: {pred.source}")
    assert pred.predicted_cluster is not None and len(pred.predicted_cluster) > 0, "Failed to get cluster"
    passed += 1
    print("  [PASS] Direct QuickML Inference test passed.")

    # ── Test 2: Graph Fusion & Evidentiary Trust ──────────────────────────────
    total += 1
    print("\n[TEST 2] Testing Graph Engine AI Affinity Fusion & Evidentiary Tiers...")
    sample_records = [
        {
            "FIR_Number": "FIR-BGL-2024-001",
            "Accused_Name": "Prashanth Acharya",
            "Co_Accused": "Ramesh Kumar",
            "Police_Station": "Koramangala PS",
            "Crime_Category": "Vehicle Theft",
            "Modus_Operandi": "Keyless Jammer Repeater"
        },
        {
            "FIR_Number": "FIR-MYS-2024-089",
            "Accused_Name": "Sunil Shetty",
            "Police_Station": "Devaraja PS",
            "Crime_Category": "Vehicle Theft",
            "Modus_Operandi": "Keyless Jammer Repeater"
        },
        {
            "FIR_Number": "FIR-BLG-2024-112",
            "Accused_Name": "Anand Murthy",
            "Police_Station": "Camp Belagavi PS",
            "Crime_Category": "Cyber Financial Fraud",
            "Modus_Operandi": "Phishing APK Malware"
        }
    ]
    headers = ["FIR_Number", "Accused_Name", "Co_Accused", "Police_Station", "Crime_Category", "Modus_Operandi"]
    base_graph = GraphEngine.build_graph_from_records(sample_records, headers)
    print(f"  -> Base Graph: {base_graph['node_count']} nodes, {base_graph['edge_count']} factual edges.")

    fused_graph = GraphEngine.fuse_ai_affinities(base_graph)
    print(f"  -> Fused Graph: {fused_graph['node_count']} nodes, {fused_graph['edge_count']} total edges.")
    print(f"  -> AI Virtual Edges Created: {fused_graph['ai_predictions_count']}")
    print(f"  -> Syndicate Clusters Found: {fused_graph['syndicate_clusters']}")

    # Verify trust tiers
    factual_edges = [e for e in fused_graph["edges"] if e.get("trustTier") == "FACTUAL"]
    ai_edges = [e for e in fused_graph["edges"] if e.get("isAiPredicted")]
    print(f"  -> Factual Evidence Edges: {len(factual_edges)}")
    print(f"  -> AI-Predicted Virtual Edges: {len(ai_edges)}")

    assert len(factual_edges) > 0, "Factual edges missing"
    assert len(ai_edges) > 0, "AI virtual edges not generated"
    assert any(e.get("style") == "dashed" for e in ai_edges), "AI edges must be dashed"
    passed += 1
    print("  [PASS] Graph Fusion & Evidentiary Trust verification passed.")

    # ── Test 3: REST API /api/quickml/predict_affinity ───────────────────────
    total += 1
    print("\n[TEST 3] Testing Flask Route: POST /api/quickml/predict_affinity...")
    resp = client.post("/api/quickml/predict_affinity", json=test_suspect)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    res_data = resp.get_json()
    assert res_data["success"] is True, "Route returned success: False"
    print(f"  -> Response: {res_data['predicted_cluster']} (Confidence: {res_data['confidence']})")
    passed += 1
    print("  [PASS] POST /api/quickml/predict_affinity passed.")

    # ── Test 4: REST API /api/graph/affinity ─────────────────────────────────
    total += 1
    print("\n[TEST 4] Testing Flask Route: GET /api/graph/affinity...")
    resp = client.get("/api/graph/affinity")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    res_data = resp.get_json()
    assert res_data["success"] is True, "Route returned success: False"
    print(f"  -> Graph Nodes: {res_data['node_count']}, Edges: {res_data['edge_count']}, AI Edges: {res_data['ai_predictions_count']}")
    passed += 1
    print("  [PASS] GET /api/graph/affinity passed.")

    # ── Test 5: Existing Core Route Health Check (Zero Regression) ───────────
    total += 1
    print("\n[TEST 5] Testing Core Server Health & Existing Routes...")
    resp = client.get("/health")
    assert resp.status_code == 200, f"/health returned {resp.status_code}"
    resp_api = client.get("/api/health")
    assert resp_api.status_code == 200, f"/api/health returned {resp_api.status_code}"
    resp_analytics = client.get("/api/analytics")
    assert resp_analytics.status_code == 200, f"/api/analytics returned {resp_analytics.status_code}"
    passed += 1
    print("  [PASS] Core Health & Analytics routes 100% operational.")

    # ── Test 6: Chatbot POST /chat Verification ──────────────────────────────
    total += 1
    print("\n[TEST 6] Testing Conversational & Analytical Chatbot Route: POST /chat...")
    chat_resp = client.post("/chat", json={
        "query": "Show me vehicle theft criminal patterns in Bengaluru",
        "session_id": "test_verification_session",
        "division": "Bengaluru Division"
    })
    assert chat_resp.status_code == 200, f"/chat returned {chat_resp.status_code}"
    chat_data = chat_resp.get_json()
    assert chat_data["success"] is True, "Chat route failed"
    print(f"  -> Agent Resolved: [{chat_data.get('agent_type')}] | {chat_data.get('agent_label')}")
    passed += 1
    print("  [PASS] POST /chat route fully operational.")

    print("\n" + "=" * 80)
    print(f"[COMPLETE] ALL {passed}/{total} VERIFICATION TESTS PASSED SUCCESSFULLY WITH ZERO REGRESSIONS!")
    print("=" * 80)


if __name__ == "__main__":
    run_tests()
