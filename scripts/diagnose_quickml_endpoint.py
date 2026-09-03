import os
import sys
import requests
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.config import (
    CATALYST_QUICKML_GEOSPATIAL_ENDPOINT,
    CATALYST_QUICKML_GEOSPATIAL_KEY,
    CATALYST_QUICKML_ORG,
    CATALYST_QUICKML_ENV,
    ZOHO_ACCESS_TOKEN_QUICKML
)
from app.services.zoho_token_manager import zoho_token_manager

endpoint = CATALYST_QUICKML_GEOSPATIAL_ENDPOINT
key = CATALYST_QUICKML_GEOSPATIAL_KEY
org = str(CATALYST_QUICKML_ORG)
env = CATALYST_QUICKML_ENV

payload = {"data": {"latitude": 12.9716, "longitude": 77.5946, "severity_weight": 75}}

print("=== DIAGNOSING QUICKML CLOUD ENDPOINT AUTHENTICATION ===")
print("Endpoint:", endpoint)
print("Key:", key[:15] + "...")
print("Org:", org)

# Test Variant 1: Key + OAuth token
tok_qm = zoho_token_manager.get_valid_token(purpose="quickml")
h1 = {
    "X-QUICKML-ENDPOINT-KEY": key,
    "CATALYST-ORG": org,
    "Environment": env,
    "Content-Type": "application/json",
    "Authorization": f"Zoho-oauthtoken {tok_qm}"
}
r1 = requests.post(endpoint, headers=h1, json=payload, timeout=5)
print(f"Variant 1 (Key + QuickML OAuth Token): Status={r1.status_code}, Body={r1.text[:200]}")

# Test Variant 2: Projects OAuth token
tok_proj = zoho_token_manager.get_valid_token(purpose="projects")
h2 = {
    "X-QUICKML-ENDPOINT-KEY": key,
    "CATALYST-ORG": org,
    "Environment": env,
    "Content-Type": "application/json",
    "Authorization": f"Zoho-oauthtoken {tok_proj}"
}
r2 = requests.post(endpoint, headers=h2, json=payload, timeout=5)
print(f"Variant 2 (Key + Projects OAuth Token): Status={r2.status_code}, Body={r2.text[:200]}")

# Test Variant 3: Key only (No Authorization header)
h3 = {
    "X-QUICKML-ENDPOINT-KEY": key,
    "CATALYST-ORG": org,
    "Environment": env,
    "Content-Type": "application/json"
}
r3 = requests.post(endpoint, headers=h3, json=payload, timeout=5)
print(f"Variant 3 (Key Only): Status={r3.status_code}, Body={r3.text[:200]}")

# Test Variant 4: CATALYST-API-KEY header
h4 = {
    "CATALYST-API-KEY": key,
    "CATALYST-ORG": org,
    "Environment": env,
    "Content-Type": "application/json"
}
r4 = requests.post(endpoint, headers=h4, json=payload, timeout=5)
print(f"Variant 4 (CATALYST-API-KEY Only): Status={r4.status_code}, Body={r4.text[:200]}")
