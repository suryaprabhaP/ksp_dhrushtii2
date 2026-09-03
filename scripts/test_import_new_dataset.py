import os
import sys
import json
import time
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import (
    ZOHO_ANALYTICS_API_BASE,
    ZOHO_ANALYTICS_WORKSPACE_ID,
    ZOHO_ANALYTICS_ORG_ID
)
from app.services.zoho_token_manager import zoho_token_manager
from app.services.zoho_analytics_service import zoho_analytics_service

print("=" * 75)
print("TESTING ZOHO ANALYTICS DATASET INGESTION: karnataka_synthetic_crimes.csv")
print("=" * 75)

csv_path = "d:/latest_datathon/rohith_project/karnataka_synthetic_crimes.csv"
if not os.path.exists(csv_path):
    print("Error: CSV file not found at", csv_path)
    sys.exit(1)

with open(csv_path, "rb") as f:
    csv_bytes = f.read()

lines_count = len(csv_bytes.decode('utf-8', errors='replace').splitlines()) - 1
print(f"Loaded dataset: 'karnataka_synthetic_crimes.csv' ({lines_count} records, {len(csv_bytes)} bytes)")

token = zoho_token_manager.get_valid_token(purpose="analytics")
print(f"Acquired Analytics Token: {token[:15]}...")

# 1. Test Bulk Import endpoint to create new table 'ksp_karnataka_crimes_500'
table_name = "ksp_karnataka_crimes_500"
url = f"{ZOHO_ANALYTICS_API_BASE}/workspaces/{ZOHO_ANALYTICS_WORKSPACE_ID}/data"

headers = {
    "Authorization": f"Zoho-oauthtoken {token}",
    "ZANALYTICS-ORGID": str(ZOHO_ANALYTICS_ORG_ID)
}

config = {
    "tableName": table_name,
    "fileType": "csv",
    "autoIdentify": True,
    "onError": "skiprow"
}

print(f"\nSending POST request to {url} to import new table '{table_name}'...")
files = {
    "FILE": ("karnataka_synthetic_crimes.csv", csv_bytes, "text/csv")
}
data = {
    "CONFIG": json.dumps(config)
}

t0 = time.time()
res = requests.post(url, headers=headers, data=data, files=files, timeout=30)
t1 = time.time()

print(f"Status Code: {res.status_code} | Latency: {(t1 - t0):.3f}s")
try:
    resp_json = res.json()
    print("Response JSON:\n", json.dumps(resp_json, indent=2))
except Exception:
    print("Raw Response:\n", res.text[:500])

# 2. List views in workspace to verify the new table exists
print("\n" + "-" * 75)
print("Introspecting Workspace Views after Import...")
time.sleep(2)
views = zoho_analytics_service.list_views()
new_view_id = None
for v in views:
    print(f" - View ID: {v.get('viewId')} | Name: {v.get('viewName')} | Type: {v.get('viewType')}")
    if v.get('viewName') == table_name:
        new_view_id = v.get('viewId')

# 3. If new view created, test generating dynamic embed URL for it!
if new_view_id:
    print(f"\n[SUCCESS] New Table '{table_name}' Created in Zoho Analytics! View ID: {new_view_id}")
    print(f"Testing Dynamic Embed URL generation for newly created table...")
    embed_res = zoho_analytics_service.get_dashboard_embed_url(view_id=new_view_id)
    print("Dynamic Embed Result:\n", json.dumps(embed_res, indent=2))
else:
    print(f"\nNotice: Table '{table_name}' not listed as separate view or pending import processing.")

print("\n" + "=" * 75)
print("IMPORT & TEST PROCESS FINISHED")
print("=" * 75)
