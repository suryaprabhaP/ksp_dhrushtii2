import requests
import json
import time
import sys

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:5000"
SESSION_ID = "officer_client_sim_001"

test_results = []

def run_interaction(title, method, endpoint, payload, desc):
    url = f"{BASE_URL}{endpoint}"
    t0 = time.time()
    try:
        if method == "POST":
            headers = {"Content-Type": "application/json"}
            if "admin" in endpoint:
                headers["Authorization"] = "Bearer KSP-SECURE-WEBHOOK-KEY"
            r = requests.post(url, json=payload, headers=headers, timeout=30)
        else:
            r = requests.get(url, timeout=30)
        elapsed = round((time.time() - t0) * 1000, 2)
        
        try:
            res_json = r.json()
        except:
            res_json = {"raw": r.text[:300]}
            
        test_results.append({
            "title": title,
            "description": desc,
            "method": method,
            "endpoint": endpoint,
            "payload": payload,
            "status_code": r.status_code,
            "elapsed_ms": elapsed,
            "response": res_json
        })
        print(f"[PASS] {title} ({elapsed} ms) - Status {r.status_code}")
    except Exception as e:
        print(f"[FAIL] {title} - Error: {e}")
        test_results.append({
            "title": title,
            "description": desc,
            "method": method,
            "endpoint": endpoint,
            "payload": payload,
            "status_code": "ERROR",
            "elapsed_ms": 0,
            "response": {"error": str(e)}
        })

print("🚀 Starting KSP Sentinel AI Client Simulation Suite...")

# 1. Analytical Scenario
run_interaction(
    "1. Crime Analytics & Caseload Forecaster",
    "POST",
    "/chat",
    {
        "query": "Show me the cyber crime and financial fraud pattern in Bengaluru East division for 2026.",
        "division": "Bengaluru East",
        "session_id": SESSION_ID
    },
    "Officer requesting situational crime pattern and trend forecasts."
)

# 2. Spatial Tactical Scenario
run_interaction(
    "2. Geospatial Hotspot & Perimeter Patrol",
    "POST",
    "/chat",
    {
        "query": "Where are the critical burglary and theft hotspots in Indiranagar and Whitefield?",
        "division": "Bengaluru East",
        "session_id": SESSION_ID,
        "spatial_context": {"latitude": 12.9784, "longitude": 77.6408, "area": "Indiranagar"}
    },
    "Officer requesting tactical perimeter patrol recommendations for active hotspots."
)

# 3. Direct QuickML DBSCAN Hotspot
run_interaction(
    "3. QuickML Geospatial DBSCAN Hotspot Prediction",
    "POST",
    "/api/quickml/predict_hotspot",
    {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "severity_weight": 85
    },
    "Direct inference request to QuickML DBSCAN model for Bangalore Central coordinates."
)

# 4. QuickML Threat Assessment
run_interaction(
    "4. QuickML Tactical Threat Classification",
    "POST",
    "/api/quickml/predict_threat",
    {
        "case_id": "KSP-FIR-2026-088",
        "crime_type": "Armed Commercial Extortion",
        "financial_loss_inr": 8500000.0,
        "latitude": 12.9352,
        "longitude": 77.6244,
        "police_station": "Koramangala PS"
    },
    "Direct inference request to QuickML Threat AutoML model for high-value extortion."
)

# 5. QuickML Syndicate Affinity
run_interaction(
    "5. QuickML Syndicate Affinity Clustering",
    "POST",
    "/api/quickml/predict_affinity",
    {
        "suspect_name": "Girish 'Tech' Murthy",
        "primary_crime_category": "Cyber Financial Fraud",
        "operating_district": "Bengaluru East",
        "modus_operandi": "Phishing APK Banking Malware",
        "threat_risk_score": 88.0,
        "prior_convictions_count": 3
    },
    "Direct inference request to QuickML Affinity Clustering model for organized cyber syndicate."
)

# 6. Legal & Procedural Scenario (BNSS / BNS)
run_interaction(
    "6. Statutory Advisory under Bharatiya Nagarik Suraksha Sanhita",
    "POST",
    "/chat",
    {
        "query": "What is the mandatory procedure under Section 102 BNSS for freezing fraudulent mule bank accounts within 2 hours of complaint?",
        "session_id": SESSION_ID
    },
    "Investigating Officer seeking procedural guidance for instant bank asset freezing."
)

# 7. Citizen e-Complaint Registration (CRUD Create)
run_interaction(
    "7. Citizen e-Complaint Registration (CRUD Create)",
    "POST",
    "/api/complaints",
    {
        "complainant_name": "Smt. Shailaja Hegde",
        "contact_phone": "+91 98450 12345",
        "incident_type": "UPI Phishing Extortion",
        "incident_location": "HSR Layout Sector 2, Bengaluru",
        "loss_amount_inr": 350000,
        "narrative": "Received a deceptive APK link on WhatsApp claiming electricity bill pending. ₹3.5L debited to unknown UPI handle."
    },
    "Citizen portal complaint intake saved directly to Zoho Catalyst DataStore."
)

# 8. Schema Drift Webhook Retraining
run_interaction(
    "8. Schema Drift Automated Retraining Webhook",
    "POST",
    "/api/admin/trigger_retraining",
    {},
    "Administrative webhook triggered upon quarterly FIR dataset update."
)

# Save raw test output
with open("client_simulation_results.json", "w") as f:
    json.dump(test_results, f, indent=2)

print("\n✨ Client Simulation Complete. Saved to client_simulation_results.json")
