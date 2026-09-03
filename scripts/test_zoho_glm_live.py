import os
import sys
import json
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import CATALYST_GLM_ENDPOINT, CATALYST_GLM_MODEL, CATALYST_ORG_ID, CATALYST_PROJECT_ID
from app.services.zoho_token_manager import zoho_token_manager

token = zoho_token_manager.get_valid_token(purpose="quickml", force_refresh=True)
print(f"QuickML Token: {token[:15]}...{token[-5:]}" if token else "No Token!")

url = CATALYST_GLM_ENDPOINT
print("Endpoint:", url)
print("Model:", CATALYST_GLM_MODEL)
print("CATALYST-ORG:", CATALYST_ORG_ID)

headers = {
    "Authorization": f"Zoho-oauthtoken {token}",
    "CATALYST-ORG": str(CATALYST_ORG_ID),
    "Content-Type": "application/json"
}

body = {
    "model": CATALYST_GLM_MODEL,
    "messages": [
        {"role": "system", "content": "You are KSP Sentinel AI."},
        {"role": "user", "content": "Hello"}
    ],
    "max_tokens": 100,
    "temperature": 0.4
}

res = requests.post(url, headers=headers, json=body, timeout=15)
print("HTTP Status:", res.status_code)
print("Headers:", dict(res.headers))
print("Response Body:", res.text)
