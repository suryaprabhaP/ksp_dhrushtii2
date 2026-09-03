"""
KSP Sentinel AI — Automated Grant Code to Refresh Token Exchanger
==================================================================
Converts a temporary Zoho Grant Code into a permanent Refresh Token
and Access Token, then automatically updates .env.standalone.
"""
import os
import sys
from pathlib import Path
import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import (
    ZOHO_CLIENT_ID,
    ZOHO_CLIENT_SECRET,
    ENV_PATH,
)

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def exchange_code(purpose: str, grant_code: str, redirect_uri: str = "http://localhost:5000/callback") -> dict:
    """
    Exchanges a single-use Grant Code with Zoho Accounts API to receive:
    1. access_token (valid for 1 hour)
    2. refresh_token (permanent)
    """
    url = "https://accounts.zoho.in/oauth/v2/token"
    params = {
        "grant_type": "authorization_code",
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "code": grant_code.strip()
    }

    print(f"[*] Contacting Zoho Accounts to exchange grant code for purpose '{purpose}'...")
    res = requests.post(url, data=params, timeout=10)
    data = res.json()

    if res.status_code == 200 and "refresh_token" in data:
        ref_tok = data["refresh_token"]
        acc_tok = data.get("access_token", "")
        print(f"✅ Success! Refresh Token acquired for '{purpose}'.")
        print(f"   Refresh Token: {ref_tok}")
        print(f"   Access Token:  {acc_tok}")

        # Update .env.standalone
        env_file = Path(ENV_PATH)
        if env_file.exists():
            content = env_file.read_text(encoding="utf-8")
            # Map purpose to env var names
            var_ref = f"ZOHO_REFRESH_TOKEN_{purpose.upper()}"
            var_acc = f"ZOHO_ACCESS_TOKEN_{purpose.upper()}"
            
            import re
            if re.search(rf"^{var_ref}=.*$", content, re.MULTILINE):
                content = re.sub(rf"^{var_ref}=.*$", f"{var_ref}={ref_tok}", content, flags=re.MULTILINE)
            else:
                content += f"\n{var_ref}={ref_tok}"

            if re.search(rf"^{var_acc}=.*$", content, re.MULTILINE):
                content = re.sub(rf"^{var_acc}=.*$", f"{var_acc}={acc_tok}", content, flags=re.MULTILINE)
            else:
                content += f"\n{var_acc}={acc_tok}"

            env_file.write_text(content, encoding="utf-8")
            print(f"💾 Updated {var_ref} and {var_acc} in .env.standalone!")

        return data
    else:
        print(f"❌ Error exchanging code for '{purpose}': {data}")
        return data


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/exchange_grant_code.py <purpose> <grant_code>")
        print("Purposes: projects | tables | cache | quickml | zia")
        sys.exit(1)

    purpose_arg = sys.argv[1].lower()
    code_arg = sys.argv[2]
    exchange_code(purpose_arg, code_arg)
