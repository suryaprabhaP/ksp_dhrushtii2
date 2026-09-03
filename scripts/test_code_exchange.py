import os
import requests
from dotenv import load_dotenv

load_dotenv("d:/latest_datathon/rohith_project/.env.standalone")

client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
token_q = os.getenv("ZOHO_REFRESH_TOKEN_QUICKML")
token_z = os.getenv("ZOHO_REFRESH_TOKEN_ZIA")

url = "https://accounts.zoho.in/oauth/v2/token"

# 1. Test as authorization_code (Grant Token)
for name, tok in [("QUICKML", token_q), ("ZIA", token_z)]:
    print(f"\n--- Trying {name} as authorization_code ---")
    data = {
        "code": tok,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code"
    }
    r = requests.post(url, data=data)
    print(f"Status: {r.status_code}, Body: {r.text}")

# 2. Test directly as Access Token on Zia STT
for name, tok in [("QUICKML", token_q), ("ZIA", token_z)]:
    print(f"\n--- Trying {name} directly as Access Token on Zia STT ---")
    stt_url = "https://api.catalyst.zoho.in/quickml/api/v1/models/zia/audio/transcribe"
    headers = {
        "CATALYST-ORG": os.getenv("CATALYST_ORG_ID", "60077159195"),
        "Authorization": f"Zoho-oauthtoken {tok}"
    }
    from scripts.test_cloud_stt_live import create_synthetic_wav_bytes
    wav = create_synthetic_wav_bytes(1.0, 440.0)
    files = {"file": ("audio.wav", wav, "audio/wav")}
    data = {"language": "en"}
    r = requests.post(stt_url, headers=headers, files=files, data=data)
    print(f"Status: {r.status_code}, Body: {r.text}")
