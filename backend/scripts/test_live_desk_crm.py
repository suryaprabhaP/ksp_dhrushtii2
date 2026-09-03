import os
import sys
import logging
import requests
from dotenv import load_dotenv

# Ensure app path is available
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.zoho_token_manager import zoho_token_manager


logging.basicConfig(level=logging.INFO)
log = logging.getLogger("test_desk_crm")

def run_diagnostics():
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.standalone'))
    
    log.info("Starting Live CRM/Desk Connectivity Test...")
    
    # 1. Get the access token via the manager (using projects token fallback)
    try:
        access_token = zoho_token_manager.get_valid_token(purpose="projects")
        if not access_token:
            log.error("Failed to retrieve a valid access token.")
            return
        log.info(f"Successfully retrieved Access Token (starts with {access_token[:10]}...)")
    except Exception as e:
        log.error(f"Error fetching token: {e}")
        return

    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }

    # 2. Test Zoho Desk (Tickets)
    desk_url = "https://desk.zoho.in/api/v1/tickets"
    log.info(f"Testing Zoho Desk API: GET {desk_url}")
    try:
        response = requests.get(desk_url, headers=headers, params={"limit": 1})
        log.info(f"Zoho Desk Status: {response.status_code}")
        if response.status_code == 200:
            log.info(f"Zoho Desk Response: {response.json().get('data', [])[:1]}")
        else:
            log.error(f"Zoho Desk Error: {response.text}")
    except Exception as e:
        log.error(f"Zoho Desk Request Failed: {e}")

    # 3. Test Zoho CRM (Leads/Suspects)
    crm_url = "https://www.zohoapis.in/crm/v3/Leads"
    log.info(f"Testing Zoho CRM API: GET {crm_url}")
    try:
        response = requests.get(crm_url, headers=headers, params={"per_page": 1})
        log.info(f"Zoho CRM Status: {response.status_code}")
        if response.status_code == 200:
            log.info(f"Zoho CRM Response: {response.json().get('data', [])[:1]}")
        else:
            log.error(f"Zoho CRM Error: {response.text}")
    except Exception as e:
        log.error(f"Zoho CRM Request Failed: {e}")

if __name__ == "__main__":
    run_diagnostics()
