import os
import sys
from pathlib import Path
import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import (
    CATALYST_API_BASE,
    CATALYST_PROJECT_ID,
    CATALYST_CACHE_SEGMENT_ID,
    CATALYST_ORG_ID
)
from app.services.zoho_token_manager import token_manager

token = token_manager.get_access_token("cache")
print(f"Token acquired: {token[:15]}...")

headers = {
    "Authorization": f"Zoho-oauthtoken {token}",
    "CATALYST-ORG": str(CATALYST_ORG_ID)
}

base_url = f"{CATALYST_API_BASE}/baas/v1/project/{CATALYST_PROJECT_ID}/segment/{CATALYST_CACHE_SEGMENT_ID}/cache"
print(f"Testing Cache URL: {base_url}")

# 1. Test GET with cacheKey
r_get = requests.get(base_url, headers=headers, params={"cacheKey": "ping_test"}, timeout=10)
print(f"GET Status: {r_get.status_code}, Response: {r_get.text[:120]}")

# 2. Test POST / PUT
payload = {
    "cache_name": "ping_test",
    "cache_value": "hello_catalyst_cache",
    "expiry_in_hours": 1
}
r_post = requests.post(base_url, headers={**headers, "Content-Type": "application/json"}, json=payload, timeout=10)
print(f"POST Status: {r_post.status_code}, Response: {r_post.text[:120]}")

if r_post.status_code != 200:
    # Try alternate payload format: cacheKey / cacheValue
    payload2 = {
        "cacheKey": "ping_test",
        "cacheValue": "hello_catalyst_cache"
    }
    r_post2 = requests.post(base_url, headers={**headers, "Content-Type": "application/json"}, json=payload2, timeout=10)
    print(f"POST (alternate payload) Status: {r_post2.status_code}, Response: {r_post2.text[:120]}")

# 3. Test GET again after insert
r_get2 = requests.get(base_url, headers=headers, params={"cacheKey": "ping_test"}, timeout=10)
print(f"GET (after write) Status: {r_get2.status_code}, Response: {r_get2.text[:120]}")
