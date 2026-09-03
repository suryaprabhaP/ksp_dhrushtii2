import os
import sys
import requests

# Ensure project root is on sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.zoho_token_manager import zoho_token_manager
from app.config import CATALYST_PROJECT_ID, CATALYST_API_BASE

token = zoho_token_manager.get_valid_token(purpose="tables", force_refresh=True)
headers = {
    "Authorization": f"Zoho-oauthtoken {token}",
    "Content-Type": "application/json"
}

print(f"Querying Catalyst AppSail services for Project: {CATALYST_PROJECT_ID}...")

# 1. Get appsail list
url = f"{CATALYST_API_BASE}/baas/v1/project/{CATALYST_PROJECT_ID}/appsail"
resp = requests.get(url, headers=headers)
print(f"AppSail List Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json().get("data", [])
    print(f"Found {len(data)} AppSail instances:")
    for app in data:
        print(f" - Name: {app.get('appsail_name')} | ID: {app.get('appsail_id')} | Status: {app.get('status')} | URL: {app.get('domain_url') or app.get('access_url')}")
else:
    print(f"Response: {resp.text}")

# 2. Get webapp list (client)
url_web = f"{CATALYST_API_BASE}/baas/v1/project/{CATALYST_PROJECT_ID}/webapp"
resp_web = requests.get(url_web, headers=headers)
print(f"\nWeb Client Status: {resp_web.status_code}")
if resp_web.status_code == 200:
    data_web = resp_web.json().get("data", [])
    print(f"Found Web Client deployments:")
    for w in data_web:
        print(f" - App: {w.get('app_name')} | Access URL: {w.get('access_url')} | Status: {w.get('status')}")
