import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv(".env.standalone")

client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
refresh_token = os.getenv("ZOHO_REFRESH_TOKEN_QUICKML")

# Fetch fresh access token
token_res = requests.post(
    "https://accounts.zoho.in/oauth/v2/token",
    params={
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }
).json()

access_token = token_res.get("access_token")
print(f"Fresh Access Token Acquired: {access_token[:25]}...")

org = "60077159195"
env = "Development"

endpoints_to_test = [
    {
        "name": "1. Geospatial DBSCAN Hotspot Clustering",
        "url": "https://api.catalyst.zoho.in/quickml/v1/project/54626000000013049/endpoints/predict",
        "key": os.getenv("CATALYST_QUICKML_GEOSPATIAL_KEY", "0742765af06e9105d37e37aaf7c40df3f501611b15735dceb35a16994c1be2dde60c4c342faf4212c5fe4087991c9b8c"),
        "payload": {
            "data": {
                "latitude": 12.981073,
                "longitude": 77.740961,
                "severity_weight": 51
            }
        }
    },
    {
        "name": "2. Threat Assessment AutoML",
        "url": "https://api.catalyst.zoho.in/quickml/v1/project/54626000000013049/endpoints/predict?explainModel=true",
        "key": os.getenv("CATALYST_QUICKML_THREAT_KEY", "27c18dcf8bef3f23b759afe09b45dc561752b6a71a290330cf990df34074bbd8e5db6bf813b9400704f9dd98e0e9646f"),
        "payload": {
            "data": {
                "case_id": "KSP-GEO-00399",
                "incident_date": "2025-04-18",
                "crime_type": "Burglary",
                "latitude": 13.322197,
                "longitude": 74.715286,
                "nearest_city": "Udupi",
                "police_station": "Udupi Town PS",
                "case_status": "Under Investigation",
                "financial_loss_inr": 4233614
            }
        }
    },
    {
        "name": "3. Crime Statistics Caseload Regression",
        "url": "https://api.catalyst.zoho.in/quickml/v1/project/54626000000013049/endpoints/predict?explainModel=true",
        "key": os.getenv("CATALYST_QUICKML_CRIMESTATS_KEY", "a908dcf3cf420bd75fda737198d374259529cd975a40b9e219b959eb93e233aea4f87115161611cd6be123b22858d8e3"),
        "payload": {
            "data": {
                "crime_subcategory": "Commercial",
                "crime_year": 2026,
                "crime_category": "Burglary",
                "crime_month": "September"
            }
        }
    },
    {
        "name": "4. Suspect Syndicate Affinity Clustering",
        "url": "https://api.catalyst.zoho.in/quickml/v1/project/54626000000013049/endpoints/predict?explainModel=true",
        "key": os.getenv("CATALYST_QUICKML_AFFINITY_KEY", "e06f95ade18d6175a8458f02ef92a41daf2f46285034ba6d259dd3ba95a1b4dd12586db0f4e776d16e140bb40e8779fd"),
        "payload": {
            "data": {
                "modus_operandi": "Gas Cutter ATM Heist",
                "district": "Bengaluru Urban",
                "crime_head": "Robbery",
                "ipc_section": "392",
                "gang_association": "D-Company_Faction_A"
            }
        }
    }
]

print("\n" + "=" * 80)
print("LIVE ZOHO CATALYST QUICKML PREDICTION ENDPOINTS TEST (NO FALLBACK)")
print("=" * 80)

for ep in endpoints_to_test:
    headers = {
        "X-QUICKML-ENDPOINT-KEY": ep["key"],
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "CATALYST-ORG": org,
        "Environment": env,
        "Content-Type": "application/json"
    }
    r = requests.post(ep["url"], headers=headers, json=ep["payload"], timeout=10)
    print(f"\n{ep['name']}")
    print(f"URL: {ep['url']}")
    print(f"HTTP Status: {r.status_code}")
    print(f"Cloud Response Body: {r.text}")
