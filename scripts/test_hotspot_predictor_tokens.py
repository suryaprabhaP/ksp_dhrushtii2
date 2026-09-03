import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv(".env.standalone")

endpoint = "https://api.catalyst.zoho.in/quickml/v1/project/54626000000013049/endpoints/predict"
key = "0742765af06e9105d37e37aaf7c40df3f501611b15735dceb35a16994c1be2dde60c4c342faf4212c5fe4087991c9b8c"
org = "60077159195"
env = "Development"

payload = {
    "data": {
        "latitude": 12.981073,
        "longitude": 77.740961,
        "severity_weight": 51
    }
}

client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")

# Collect all refresh tokens
tokens_to_test = {
    "api_zoho": os.getenv("api_zoho"),
    "ZOHO_REFRESH_TOKEN_QUICKML": os.getenv("ZOHO_REFRESH_TOKEN_QUICKML"),
    "ZOHO_REFRESH_TOKEN_PROJECTS": os.getenv("ZOHO_REFRESH_TOKEN_PROJECTS"),
    "ZOHO_REFRESH_TOKEN_TABLES": os.getenv("ZOHO_REFRESH_TOKEN_TABLES"),
    "ZOHO_REFRESH_TOKEN_CACHE": os.getenv("ZOHO_REFRESH_TOKEN_CACHE"),
    "ZOHO_ACCESS_TOKEN_QUICKML_STATIC": os.getenv("ZOHO_ACCESS_TOKEN_QUICKML")
}

print(f"Testing Hotspot Predictor Endpoint: {endpoint}")
print(f"Endpoint Key: {key[:20]}...")
print(f"Payload: {json.dumps(payload)}")
print("-" * 60)

for name, tok in tokens_to_test.items():
    if not tok:
        continue
    access_tok = tok
    # If it's a refresh token, fetch access token
    if tok.startswith("1000.") and len(tok) > 50 and not name.endswith("_STATIC"):
        try:
            token_url = "https://accounts.zoho.in/oauth/v2/token"
            params = {
                "refresh_token": tok,
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "refresh_token"
            }
            res = requests.post(token_url, params=params, timeout=5)
            if res.status_code == 200 and "access_token" in res.json():
                access_tok = res.json()["access_token"]
                print(f"[{name}] Refreshed Access Token: {access_tok[:20]}...")
            else:
                print(f"[{name}] Token Refresh Failed: {res.text[:100]}")
                continue
        except Exception as e:
            print(f"[{name}] Error refreshing: {e}")
            continue

    headers = {
        "X-QUICKML-ENDPOINT-KEY": key,
        "Authorization": f"Zoho-oauthtoken {access_tok}",
        "CATALYST-ORG": org,
        "Environment": env,
        "Content-Type": "application/json"
    }

    try:
        r = requests.post(endpoint, headers=headers, json=payload, timeout=8)
        print(f"[{name}] HTTP {r.status_code}: {r.text}")
    except Exception as e:
        print(f"[{name}] Request Error: {e}")
