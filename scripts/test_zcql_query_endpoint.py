import os
import requests
from dotenv import load_dotenv
import sys

load_dotenv("d:/latest_datathon/rohith_project/.env.standalone")
sys.path.insert(0, "d:/latest_datathon/rohith_project/backend")

from app.services.zoho_token_manager import zoho_token_manager

project_id = os.getenv("CATALYST_PROJECT_ID", "54626000000013049")
org_id = os.getenv("CATALYST_ORG_ID", "60077159195")

for purpose in ["tables", "quickml", "zia", "cache", "projects"]:
    token = zoho_token_manager.get_valid_token(purpose=purpose)
    print(f"\n--- Testing Purpose: {purpose} (Token: {token[:20] if token else 'None'}...) ---")
    if not token:
        continue
    
    url = f"https://api.catalyst.zoho.in/baas/v1/project/{project_id}/query"
    headers = {
        "Authorization": f"Zoho-oauthtoken {token}",
        "CATALYST-ORG": str(org_id),
        "Content-Type": "application/json"
    }
    payload = {"query": "SELECT * FROM CRMSuspects"}
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:200]}")
    except Exception as e:
        print(f"Exception: {e}")
