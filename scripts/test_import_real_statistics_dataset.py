import os
import sys
import json
import time
import requests

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server import app
from app.config import (
    ZOHO_ANALYTICS_API_BASE,
    ZOHO_ANALYTICS_WORKSPACE_ID,
    ZOHO_ANALYTICS_ORG_ID
)
from app.services.zoho_token_manager import zoho_token_manager
from app.services.zoho_analytics_service import zoho_analytics_service
from app.engine.session_store import session_store

print("=" * 80)
print("TESTING DYNAMIC SCHEMA ADAPTABILITY ON REAL FORENSIC STATISTICS DATASET")
print("=" * 80)

# 1. Load real statistics dataset from real_statistics_sample_dataset
real_csv_path = "d:/latest_datathon/real_statistics_sample_dataset/8729a54d-0057-437d-8d9e-1374ef62c63f.csv"
if not os.path.exists(real_csv_path):
    print("Error: Dataset file not found at", real_csv_path)
    sys.exit(1)

with open(real_csv_path, "rb") as f:
    csv_bytes = f.read()

lines = csv_bytes.decode("utf-8", errors="replace").splitlines()
headers = lines[0].split(",")
print(f"Dataset File: 8729a54d-0057-437d-8d9e-1374ef62c63f.csv")
print(f"Total Rows: {len(lines)-1} district jurisdictions")
print("Detected Forensic Columns / Features (11):")
for h in headers:
    print(f"  • {h.strip()}")

# 2. Ingest into Zoho Analytics Cloud BI as a New Dynamic Table
table_name = "ksp_violent_crime_forensics_real"
token = zoho_token_manager.get_valid_token(purpose="analytics")

url = f"{ZOHO_ANALYTICS_API_BASE}/workspaces/{ZOHO_ANALYTICS_WORKSPACE_ID}/data"
headers_http = {
    "Authorization": f"Zoho-oauthtoken {token}",
    "ZANALYTICS-ORGID": str(ZOHO_ANALYTICS_ORG_ID)
}
config = {
    "tableName": table_name,
    "fileType": "csv",
    "autoIdentify": True,
    "onError": "skiprow"
}
files = {
    "FILE": ("violent_crime_statistics.csv", csv_bytes, "text/csv")
}
data = {
    "CONFIG": json.dumps(config)
}

print(f"\n[Step 1] Ingesting dynamic features into Zoho Analytics (Table: {table_name})...")
t0 = time.time()
res = requests.post(url, headers=headers_http, data=data, files=files, timeout=30)
t1 = time.time()

print(f"Status Code: {res.status_code} | Latency: {(t1 - t0):.3f}s")
resp_data = res.json() if res.status_code == 200 else res.text
if isinstance(resp_data, dict):
    print("Import Summary:", json.dumps(resp_data.get("data", {}).get("importSummary", {}), indent=2))
    print("Auto-Identified Column Schema Data Types:")
    print(json.dumps(resp_data.get("data", {}).get("columnDetails", {}), indent=2))
    new_view_id = resp_data.get("data", {}).get("viewId")
else:
    print("Response:", resp_data)
    new_view_id = None

# 3. Dynamic Embed URL Generation for this new feature schema
if new_view_id:
    print(f"\n[Step 2] Generating Dynamic Embed URL for View {new_view_id}...")
    embed_info = zoho_analytics_service.get_dashboard_embed_url(view_id=new_view_id)
    print("View URL:", embed_info.get("view_url"))
    print("Evidentiary Certified:", embed_info.get("evidentiary_certified"))

# 4. Ingest into Drishti Analytics Engine and Test Chatbot Response
print("\n[Step 3] Mounting New Dynamic Schema into Drishti Analytics Engine...")
session_id = "test_real_features_session"
session_store.ingest_dataset(session_id, "violent_crime_statistics.csv", csv_bytes)

print("Dispatching query to Chatbot Analytics Agent using Zoho Catalyst GLM 4.7...")
client = app.test_client()
query = "Analyze the top 5 districts with the highest Murder Rate and Causing Death by Negligence"

t0 = time.time()
chat_res = client.post("/chat", json={
    "query": query,
    "session_id": session_id,
    "division": "Karnataka State Command"
})
t1 = time.time()

print(f"Chatbot Status: {chat_res.status_code} | Latency: {(t1 - t0):.3f}s")
chat_data = chat_res.get_json() or {}

print(f"Agent Type: {chat_data.get('agent_type')}")
print(f"Provider: {chat_data.get('provider')}")
print(f"Visual Charts Generated: {len(chat_data.get('charts', []))}")
for idx, c in enumerate(chat_data.get("charts", []), 1):
    print(f"  Chart {idx}: {c.get('title')} ({c.get('type')})")

print("\nExecutive Intelligence Briefing Preview:")
print("-" * 80)
print(chat_data.get("answer", "")[:600])
print("-" * 80)

print("\n" + "=" * 80)
print("REAL FEATURE DATASET INGESTION & ANALYTICS TEST COMPLETE")
print("=" * 80)
