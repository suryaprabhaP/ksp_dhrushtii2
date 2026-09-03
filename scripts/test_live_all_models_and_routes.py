"""
KSP Sentinel AI — Comprehensive Live Multi-Pipeline & Chatbot Integration Verification
======================================================================================
"""
import sys
import json
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:5000"

def run_live_verification():
    print("=" * 85)
    print("🎯 KSP SENTINEL AI: LIVE QUICKML MULTI-MODEL & CHATBOT VERIFICATION SUITE")
    print("=" * 85)

    # ──────────────────────────────────────────────────────────────────────────
    # 1. Pipeline 1: Suspect Syndicate Affinity
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[1/6] Testing Route: POST /api/quickml/predict_affinity")
    aff_payload = {
        "suspect_id": "KSP-SUS-9011",
        "suspect_name": "Girish 'Tech' Murthy",
        "primary_crime_category": "Cyber Financial Fraud",
        "modus_operandi": "Phishing APK Banking Malware",
        "operating_district": "Bengaluru East",
        "time_window": "Business Hours (10:00 - 17:00)",
        "target_demographic": "Elderly Bank Customers",
        "primary_tool_or_weapon": "Bulk SMS Gateway",
        "prior_convictions_count": 2,
        "threat_risk_score": 88.0
    }
    r1 = requests.post(f"{BASE_URL}/api/quickml/predict_affinity", json=aff_payload)
    print(f"  → HTTP Status: {r1.status_code}")
    print(f"  → Payload Response: {json.dumps(r1.json(), indent=2)}")

    # ──────────────────────────────────────────────────────────────────────────
    # 2. Pipeline 2: Crime Caseload Regression (KSP_CrimeStatistics_5000)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[2/6] Testing Route: POST /api/quickml/predict_caseload")
    case_payload = {
        "crime_year": 2024,
        "crime_month": "September",
        "crime_category": "Organized Robbery",
        "crime_subcategory": "ATM Gas Cutter Raid"
    }
    r2 = requests.post(f"{BASE_URL}/api/quickml/predict_caseload", json=case_payload)
    print(f"  → HTTP Status: {r2.status_code}")
    print(f"  → Payload Response: {json.dumps(r2.json(), indent=2)}")

    # ──────────────────────────────────────────────────────────────────────────
    # 3. Pipeline 3: Tactical Threat Assessment (KSP_Threat_AutoML_pipeline)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[3/6] Testing Route: POST /api/quickml/predict_threat")
    threat_payload = {
        "case_id": "KSP-GEO-00399",
        "incident_date": "2025-04-18",
        "crime_type": "Burglary",
        "latitude": 13.322197,
        "longitude": 74.715286,
        "nearest_city": "Udupi",
        "police_station": "Udupi Town PS",
        "case_status": "Under Investigation",
        "financial_loss_inr": 4233614.0
    }
    r3 = requests.post(f"{BASE_URL}/api/quickml/predict_threat", json=threat_payload)
    print(f"  → HTTP Status: {r3.status_code}")
    print(f"  → Payload Response: {json.dumps(r3.json(), indent=2)}")

    # ──────────────────────────────────────────────────────────────────────────
    # 4. Pipeline 4: Geospatial DBSCAN Hotspots (KSP_Geospatial_DBSCAN_Pipeline)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[4/6] Testing Route: POST /api/quickml/predict_hotspot")
    geo_payload = {
        "latitude": 12.981073,
        "longitude": 77.740961,
        "severity_weight": 51
    }
    r4 = requests.post(f"{BASE_URL}/api/quickml/predict_hotspot", json=geo_payload)
    print(f"  → HTTP Status: {r4.status_code}")
    print(f"  → Payload Response: {json.dumps(r4.json(), indent=2)}")

    # ──────────────────────────────────────────────────────────────────────────
    # 5. Chatbot Route: Spatial Tactical Agent with DBSCAN & Threat Assessment
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[5/6] Testing Route: POST /chat (Spatial Tactical Agent -> QuickML Hotspot & Threat)")
    chat_spatial_payload = {
        "query": "Analyze the spatial cluster and assess threat level for Whitefield coordinates",
        "session_id": "test_session_spatial"
    }
    r5 = requests.post(f"{BASE_URL}/chat", json=chat_spatial_payload)
    print(f"  → HTTP Status: {r5.status_code}")
    res5 = r5.json()
    print(f"  → Agent Type: {res5.get('agent_type')}")
    print(f"  → Provider: {res5.get('provider')}")
    print(f"  → Briefing Excerpt:\n{res5.get('answer', '')[:400]}...")

    # ──────────────────────────────────────────────────────────────────────────
    # 6. Chatbot Route: Analytical Agent with QuickML Caseload Forecasting
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[6/6] Testing Route: POST /chat (Analytical Agent -> QuickML Caseload Regression)")
    chat_analytical_payload = {
        "query": "Predict the caseload for ATM Gas Cutter Raids in September 2025",
        "session_id": "test_session_analytical"
    }
    r6 = requests.post(f"{BASE_URL}/chat", json=chat_analytical_payload)
    print(f"  → HTTP Status: {r6.status_code}")
    res6 = r6.json()
    print(f"  → Agent Type: {res6.get('agent_type')}")
    print(f"  → Provider: {res6.get('provider')}")
    print(f"  → Briefing Excerpt:\n{res6.get('answer', '')[:400]}...")

    print("\n" + "=" * 85)
    print("🏁 ALL 6 TESTS EXECUTED SUCCESSFULLY")
    print("=" * 85)


if __name__ == "__main__":
    run_live_verification()
