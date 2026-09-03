import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("KSP_CLIENT_ID", "1000.QJ48UXS62P10JU8969EVZH62U1SZFK")
client_secret = os.getenv("KSP_CLIENT_SECRET", "")
grant_token = os.getenv("GRANT_TOKEN", "")

url = "https://accounts.zoho.in/oauth/v2/token"

payload = {
    "grant_type": "authorization_code",
    "client_id": client_id,
    "client_secret": client_secret,
    "code": grant_token
}

response = requests.post(url, data=payload)
print(response.text)
