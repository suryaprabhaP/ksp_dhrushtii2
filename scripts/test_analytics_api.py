import os
import requests
import json
from dotenv import load_dotenv

load_dotenv("d:/latest_datathon/rohith_project/.env.standalone")

workspace_id = os.getenv("ZOHO_ANALYTICS_WORKSPACE_ID")
access_token = "1000.4b641d00fe99494f4088b99e6422c831.16f2851c95d2ca48bac833dc2e509754"
view_id = "563936000000003002"

headers = {
    "Authorization": f"Zoho-oauthtoken {access_token}",
    "ZANALYTICS-ORGID": "60085982953",
    "Accept": "application/vnd.analytics.v2+json"
}

print(f"Testing /publish API with new embed.all scope...")
url_publish = f"https://analyticsapi.zoho.in/restapi/v2/workspaces/{workspace_id}/views/{view_id}/publish"
try:
    res = requests.get(url_publish, headers=headers)
    print("GET /publish Status:", res.status_code)
    print(json.dumps(res.json(), indent=2))
except Exception as e:
    print(e)
    
print(f"Testing /publish/embed API with new embed.all scope...")
url_embed = f"https://analyticsapi.zoho.in/restapi/v2/workspaces/{workspace_id}/views/{view_id}/publish/embed"
try:
    res = requests.get(url_embed, headers=headers)
    print("GET /publish/embed Status:", res.status_code)
    print(json.dumps(res.json(), indent=2))
except Exception as e:
    print(e)
