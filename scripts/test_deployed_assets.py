import requests
import re

base_url = "https://kspcrimeintelligenceplatform-60077159195.development.catalystserverless.in/app/"
resp = requests.get(base_url + "index.html")
print(f"HTML Status: {resp.status_code}")

assets = re.findall(r'(?:src|href)="([^"]+)"', resp.text)
print(f"Discovered {len(assets)} assets:")

for a in assets:
    if a.startswith("http") or a.startswith("//"):
        continue
    # clean leading ./
    rel_path = a.lstrip("./")
    target_url = base_url + rel_path
    asset_resp = requests.get(target_url)
    print(f" - {rel_path} -> HTTP {asset_resp.status_code} ({len(asset_resp.content)} bytes)")
