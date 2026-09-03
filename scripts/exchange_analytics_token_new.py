import requests
import json
import os
from dotenv import load_dotenv

load_dotenv("d:/latest_datathon/rohith_project/.env.standalone")

client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
grant_token = "1000.c4a536463c2e9d1b395a62fecec25fa2.1c1cc05f924f49e607022bfa45ab09a8"

url = "https://accounts.zoho.in/oauth/v2/token"

payload = {
    "grant_type": "authorization_code",
    "client_id": client_id,
    "client_secret": client_secret,
    "code": grant_token
}

print("Exchanging Grant Token...")
response = requests.post(url, data=payload)
data = response.json()
print(json.dumps(data, indent=2))

if "refresh_token" in data:
    with open("zoho_analytics_credentials.json", "w") as f:
        json.dump(data, f, indent=2)
    print("Tokens saved to zoho_analytics_credentials.json")
