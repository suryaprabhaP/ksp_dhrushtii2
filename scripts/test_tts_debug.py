import json
import os
import requests
from dotenv import load_dotenv

load_dotenv("d:/latest_datathon/rohith_project/.env.standalone")

token = os.getenv("ZOHO_ACCESS_TOKEN_QUICKML")
org_id = os.getenv("CATALYST_ORG_ID", "60077159195")
tts_url = "https://api.catalyst.zoho.in/quickml/api/v1/models/zia/tts/synthesize"

print(f"Token: {token[:12]}...")
print(f"Org ID: {org_id}")
print(f"TTS URL: {tts_url}")

headers = {
    "CATALYST-ORG": str(org_id),
    "Authorization": f"Zoho-oauthtoken {token}",
    "Content-Type": "application/json",
    "Accept": "*/*"
}

payloads = [
    {
        "name": "Hindi - Divya (Exact Sample)",
        "body": {
            "text": "भारत एक महान देश है",
            "language": "hi",
            "speaker": "Divya",
            "pitch": "moderate",
            "speed": "moderate",
            "emotion": "neutral"
        }
    },
    {
        "name": "English - Mary",
        "body": {
            "text": "Karnataka State Police Sentinel AI",
            "language": "en",
            "speaker": "Mary",
            "pitch": "moderate",
            "speed": "moderate",
            "emotion": "neutral"
        }
    },
    {
        "name": "Kannada - Anu",
        "body": {
            "text": "ಕರ್ನಾಟಕ ರಾಜ್ಯ ಪೊಲೀಸ್",
            "language": "kn",
            "speaker": "Anu",
            "pitch": "moderate",
            "speed": "moderate",
            "emotion": "neutral"
        }
    }
]

for p in payloads:
    print(f"\n--- Testing {p['name']} ---")
    try:
        r = requests.post(tts_url, headers=headers, json=p['body'], timeout=20)
        print(f"Status: {r.status_code}")
        print(f"Headers: {dict(r.headers)}")
        if r.status_code == 200:
            print(f"SUCCESS! Audio bytes received: {len(r.content)} bytes")
            print(f"X-Audio-Info: {r.headers.get('X-Audio-Info')}")
        else:
            print(f"Response text: {r.text[:300]}")
    except Exception as e:
        print(f"Exception: {e}")
