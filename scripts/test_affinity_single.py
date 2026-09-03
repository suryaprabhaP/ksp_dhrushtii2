import os
import requests
from dotenv import load_dotenv

load_dotenv(".env.standalone")
client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
refresh_token = os.getenv("ZOHO_REFRESH_TOKEN_QUICKML")

token_res = requests.post(
    "https://accounts.zoho.in/oauth/v2/token",
    params={
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }
).json()
access_token = token_res["access_token"]

url = "https://api.catalyst.zoho.in/quickml/v1/project/54626000000013049/endpoints/predict?explainModel=true"
key = os.getenv("CATALYST_QUICKML_AFFINITY_KEY", "e06f95ade18d6175a8458f02ef92a41daf2f46285034ba6d259dd3ba95a1b4dd12586db0f4e776d16e140bb40e8779fd")
headers = {
    "X-QUICKML-ENDPOINT-KEY": key,
    "Authorization": f"Zoho-oauthtoken {access_token}",
    "CATALYST-ORG": "60077159195",
    "Environment": "Development",
    "Content-Type": "application/json"
}

payload = {
    "data": {
        "suspect_id": "SUSP-10029",
        "suspect_name": "Ramesh Kumar",
        "threat_risk_score": 88,
        "target_demographic": "Jewelry Stores",
        "operating_district": "Bengaluru Urban",
        "prior_convictions_count": 4,
        "time_window": "Night",
        "primary_crime_category": "Robbery",
        "primary_tool_or_weapon": "Gas Cutter",
        "modus_operandi": "Nighttime Safe Drilling"
    }
}

r = requests.post(url, headers=headers, json=payload, timeout=10)
print("Exact Schema Payload Result:", r.status_code, r.text)
