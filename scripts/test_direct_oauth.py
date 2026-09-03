import os
import requests
from dotenv import load_dotenv

load_dotenv("d:/latest_datathon/rohith_project/.env.standalone")

client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
refresh_quickml = os.getenv("ZOHO_REFRESH_TOKEN_QUICKML")
refresh_zia = os.getenv("ZOHO_REFRESH_TOKEN_ZIA")

print("Client ID:", client_id)
print("Client Secret:", client_secret[:6] + "..." if client_secret else None)

def test_refresh(label, r_token):
    print(f"\n--- Testing Refresh for {label} ---")
    print(f"Token: {r_token}")
    url = "https://accounts.zoho.in/oauth/v2/token"
    data = {
        "refresh_token": r_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }
    res = requests.post(url, data=data)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.json()}")
    return res.json().get("access_token")

acc_q = test_refresh("QUICKML", refresh_quickml)
acc_z = test_refresh("ZIA", refresh_zia)

# Now test Zia STT endpoint with each valid access token
if acc_q:
    print("\n--- Testing Zia STT Endpoint with Fresh QUICKML Access Token ---")
    stt_url = "https://api.catalyst.zoho.in/quickml/api/v1/models/zia/audio/transcribe"
    headers = {
        "CATALYST-ORG": os.getenv("CATALYST_ORG_ID", "60077159195"),
        "Authorization": f"Zoho-oauthtoken {acc_q}"
    }
    # Create simple wav
    from scripts.test_cloud_stt_live import create_synthetic_wav_bytes
    wav = create_synthetic_wav_bytes(1.0, 440.0)
    files = {"file": ("audio.wav", wav, "audio/wav")}
    data = {"language": "en"}
    r = requests.post(stt_url, headers=headers, files=files, data=data)
    print(f"STT Status with QuickML Token: {r.status_code}")
    print(f"STT Response: {r.text}")

if acc_z:
    print("\n--- Testing Zia STT Endpoint with Fresh ZIA Access Token ---")
    stt_url = "https://api.catalyst.zoho.in/quickml/api/v1/models/zia/audio/transcribe"
    headers = {
        "CATALYST-ORG": os.getenv("CATALYST_ORG_ID", "60077159195"),
        "Authorization": f"Zoho-oauthtoken {acc_z}"
    }
    from scripts.test_cloud_stt_live import create_synthetic_wav_bytes
    wav = create_synthetic_wav_bytes(1.0, 440.0)
    files = {"file": ("audio.wav", wav, "audio/wav")}
    data = {"language": "en"}
    r = requests.post(stt_url, headers=headers, files=files, data=data)
    print(f"STT Status with Zia Token: {r.status_code}")
    print(f"STT Response: {r.text}")
