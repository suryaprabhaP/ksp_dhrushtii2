import os
import requests
from dotenv import load_dotenv

load_dotenv("d:/latest_datathon/rohith_project/.env.standalone")

token = os.getenv("ZOHO_ACCESS_TOKEN_TABLES") or os.getenv("ZOHO_ACCESS_TOKEN")
project_id = os.getenv("CATALYST_PROJECT_ID", "54626000000013049")
org_id = os.getenv("CATALYST_ORG_ID", "60077159195")

print(f"Testing with Token: {token[:20]}... Project ID: {project_id}")

candidates = [
    f"https://api.catalyst.zoho.in/baas/v1/project/{project_id}/zcql",
    f"https://api.catalyst.zoho.in/baas/v1/project/{project_id}/query",
    f"https://api.catalyst.zoho.in/catalyst/v1/project/{project_id}/zcql",
    f"https://api.catalyst.zoho.in/api/v1/project/{project_id}/zcql",
    f"https://api.catalyst.zoho.in/baas/v1/projects/{project_id}/zcql",
    f"https://api.catalyst.zoho.in/quickml/api/v1/project/{project_id}/zcql",
]

payload = {"query": "SELECT * FROM CRMSuspects"}
headers = {
    "Authorization": f"Zoho-oauthtoken {token}",
    "CATALYST-ORG": str(org_id),
    "Content-Type": "application/json"
}

for url in candidates:
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=4)
        print(f"URL: {url} -> Status: {r.status_code} -> Resp: {r.text[:120]}")
    except Exception as e:
        print(f"URL: {url} -> Exception: {e}")
