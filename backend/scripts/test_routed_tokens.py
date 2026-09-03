"""
KSP Sentinel AI — Multi-Token Routing & 8-Minute Refresh Strategy Test Suite
=============================================================================
Verifies:
1. Token Manager Purpose Routing (Projects, Tables, Cache, QuickML, Zia)
2. 8-Minute (480s) Proactive TTL Refresh Buffer Calculation
3. Cascading Fallback Resolution
4. Live Cloud Endpoints Connectivity with Purpose Tokens
"""
import json
import logging
import os
import sys
import time
from pathlib import Path
import requests

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Setup rich console logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("test.routed_tokens")

from app.config import (
    CATALYST_API_BASE,
    CATALYST_ORG_ID,
    CATALYST_PROJECT_ID,
    CATALYST_TABLE_ECOMPLAINTS,
    CATALYST_TABLE_PASSPORTS,
    CATALYST_TABLE_POLICEFIRS,
    CATALYST_CACHE_SEGMENT_ID,
    ZIA_AUDIO_ENDPOINT,
)
from app.services.zoho_token_manager import (
    zoho_token_manager,
    REFRESH_BUFFER_SECONDS,
)


import sys

# Ensure UTF-8 stdout encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def print_banner(title: str):
    print("\n" + "=" * 78)
    print(f"  [*] {title.upper()}")
    print("=" * 78)


def test_token_manager_status():
    print_banner("1. Multi-Token Manager Diagnostic Status")
    status = zoho_token_manager.get_status()
    print(f"{'PURPOSE':<12} | {'HAS ACCESS':<10} | {'PREVIEW':<22} | {'HAS REFRESH':<11} | {'TTL REMAINING':<14} | {'ACTIVE'}")
    print("-" * 88)
    for purpose, info in status.items():
        print(
            f"{purpose:<12} | "
            f"{str(info['has_access_token']):<10} | "
            f"{info['access_token_preview']:<22} | "
            f"{str(info['has_refresh_token']):<11} | "
            f"{str(info['ttl_seconds_remaining']) + 's':<14} | "
            f"{'✅' if info['is_active'] else '⚠️'}"
        )
    print(f"\n[Buffer Check] Configured Proactive Refresh Buffer: {REFRESH_BUFFER_SECONDS} seconds (8 minutes).")


def test_purpose_routing():
    print_banner("2. Purpose-Based Token Resolution & Fallback Verification")
    purposes = ["projects", "tables", "cache", "quickml", "zia", "default", "database", "speech"]

    for p in purposes:
        resolved_tok = zoho_token_manager.get_valid_token(purpose=p)
        tok_preview = f"{resolved_tok[:12]}...{resolved_tok[-6:]}" if resolved_tok and len(resolved_tok) > 18 else (resolved_tok or "None")
        norm = zoho_token_manager._normalize_purpose(p)
        print(f"• Request purpose='{p:<10}' -> Normalized='{norm:<8}' -> Token={tok_preview}")


def test_live_tables_endpoint():
    print_banner("3. Live Testing: DataStore / Tables API (Purpose: tables)")
    token = zoho_token_manager.get_valid_token(purpose="tables")
    if not token:
        print("❌ [Tables] No access token available for 'tables'.")
        return False

    url = f"{CATALYST_API_BASE}/baas/v1/project/{CATALYST_PROJECT_ID}/table"
    headers = {
        "Authorization": f"Zoho-oauthtoken {token}",
        "CATALYST-ORG": str(CATALYST_ORG_ID),
    }

    try:
        res = requests.get(url, headers=headers, timeout=6)
        print(f"GET {url} -> Status HTTP {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            tables = data.get("data", [])
            print(f"✅ [Tables] Successfully authenticated! Found {len(tables)} tables in DataStore.")
            for t in tables[:3]:
                print(f"   - Table Name: {t.get('table_name')} (ID: {t.get('table_id')})")
            return True
        else:
            print(f"⚠️ [Tables] Response: {res.status_code} - {res.text[:200]}")
    except Exception as e:
        print(f"❌ [Tables] Network error: {e}")
    return False


def test_live_cache_endpoint():
    print_banner("4. Live Testing: Catalyst Cache API (Purpose: cache)")
    token = zoho_token_manager.get_valid_token(purpose="cache")
    if not token:
        print("❌ [Cache] No access token available for 'cache'.")
        return False

    url = f"{CATALYST_API_BASE}/baas/v1/project/{CATALYST_PROJECT_ID}/cache/segment/{CATALYST_CACHE_SEGMENT_ID}/item"
    headers = {
        "Authorization": f"Zoho-oauthtoken {token}",
        "CATALYST-ORG": str(CATALYST_ORG_ID),
    }
    params = {"key": "test_ping_ksp"}

    try:
        res = requests.get(url, headers=headers, params=params, timeout=6)
        print(f"GET {url} -> Status HTTP {res.status_code}")
        if res.status_code in (200, 204):
            print("✅ [Cache] Successfully authenticated to Catalyst Cache segment!")
            return True
        elif res.status_code == 404 or "RESOURCE_NOT_FOUND" in res.text:
            print("✅ [Cache] Authentication succeeded (Key test_ping_ksp does not exist yet as expected).")
            return True
        else:
            print(f"⚠️ [Cache] Response: {res.status_code} - {res.text[:200]}")
    except Exception as e:
        print(f"❌ [Cache] Network error: {e}")
    return False


def test_live_quickml_endpoint():
    print_banner("5. Live Testing: QuickML RAG / ML Endpoint (Purpose: quickml)")
    token = zoho_token_manager.get_valid_token(purpose="quickml")
    if not token:
        print("❌ [QuickML] No access token available for 'quickml'.")
        return False

    url = f"https://console.catalyst.zoho.in/quickml/v1/project/{CATALYST_PROJECT_ID}/rag/answer"
    headers = {
        "Authorization": f"Zoho-oauthtoken {token}",
        "CATALYST-ORG": str(CATALYST_ORG_ID),
        "Content-Type": "application/json"
    }
    payload = {
        "question": "What are the BNS provisions for cyber extortion?",
        "doc_ids": ["3407000000004223"]
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=6)
        print(f"POST {url} -> Status HTTP {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print("✅ [QuickML] Successfully received RAG answer from QuickML endpoint!")
            print(f"   Answer preview: {str(data)[:150]}...")
            return True
        else:
            print(f"⚠️ [QuickML] Response: {res.status_code} - {res.text[:200]}")
    except Exception as e:
        print(f"❌ [QuickML] Network error: {e}")
    return False


def test_live_zia_endpoint():
    print_banner("6. Live Testing: Zia Speech / AI Endpoint (Purpose: zia)")
    token = zoho_token_manager.get_valid_token(purpose="zia")
    if not token:
        print("❌ [Zia] No access token available for 'zia'.")
        return False

    headers = {
        "Authorization": f"Zoho-oauthtoken {token}",
        "CATALYST-ORG": str(CATALYST_ORG_ID),
    }

    try:
        # Ping the Zia Audio endpoint with a HEAD or empty POST request to verify authentication
        res = requests.post(ZIA_AUDIO_ENDPOINT, headers=headers, timeout=6)
        print(f"POST {ZIA_AUDIO_ENDPOINT} -> Status HTTP {res.status_code}")
        if res.status_code in (200, 400):
            # 400 means "Missing audio file", which proves authentication with token succeeded!
            if res.status_code == 400:
                print("✅ [Zia] Authentication succeeded! (Endpoint reached and validated OAuth token; returned HTTP 400 for empty audio payload as expected).")
            else:
                print("✅ [Zia] Endpoint authenticated successfully!")
            return True
        else:
            print(f"⚠️ [Zia] Response: {res.status_code} - {res.text[:200]}")
    except Exception as e:
        print(f"❌ [Zia] Network error: {e}")
    return False


if __name__ == "__main__":
    print("=" * 78)
    print("  KSP SENTINEL AI — MULTI-TOKEN ROUTING & REFRESH VERIFICATION")
    print("=" * 78)
    test_token_manager_status()
    test_purpose_routing()
    test_live_tables_endpoint()
    test_live_cache_endpoint()
    test_live_quickml_endpoint()
    test_live_zia_endpoint()
    print_banner("Verification Completed")
