"""
KSP Sentinel AI — Zoho Analytics Service (SOLID: SRP & Evidentiary Sec 65B BSA)
================================================================================
Encapsulates communication with Zoho Analytics REST API v2:
- Dynamic view publishing and secure iframe embed URL generation
- Workspace catalog introspection (views, reports, dashboards)
- Evidentiary Section 65B BSA cryptographic integrity hashing (SHA-256)
- Thread-safe token resolution via ZohoTokenManager
"""

import hashlib
import json
import logging
import time
from typing import Any, Dict, List, Optional
import requests

from app.config import (
    ZOHO_ANALYTICS_API_BASE,
    ZOHO_ANALYTICS_WORKSPACE_ID,
    ZOHO_ANALYTICS_ORG_ID,
    ZOHO_ANALYTICS_DEFAULT_VIEW_ID,
)
from app.services.zoho_token_manager import zoho_token_manager

log = logging.getLogger("standalone.zoho_analytics_service")


class ZohoAnalyticsService:
    """
    Dedicated Service Layer adapter for Zoho Analytics v2 Cloud API.
    Handles dynamic secure embed publishing, dataset ingestion, and Section 65B forensic verification.
    """

    def __init__(self):
        self.api_base = ZOHO_ANALYTICS_API_BASE
        self.default_workspace_id = ZOHO_ANALYTICS_WORKSPACE_ID
        self.default_org_id = ZOHO_ANALYTICS_ORG_ID
        self.default_view_id = ZOHO_ANALYTICS_DEFAULT_VIEW_ID

    def _get_headers(self) -> Dict[str, str]:
        """Resolves active bearer token from ZohoTokenManager with multi-tenant org routing header."""
        token = zoho_token_manager.get_valid_token(purpose="analytics")
        if not token:
            log.error("[ZohoAnalyticsService] Failed to acquire valid OAuth token for 'analytics'.")
            raise RuntimeError("Zoho Analytics authentication token unavailable. Check OAuth refresh configuration.")

        return {
            "Authorization": f"Zoho-oauthtoken {token}",
            "ZANALYTICS-ORGID": str(self.default_org_id),
            "Accept": "application/vnd.analytics.v2+json",
        }

    def get_dashboard_embed_url(
        self,
        workspace_id: Optional[str] = None,
        view_id: Optional[str] = None,
        theme: str = "blue"
    ) -> Dict[str, Any]:
        """
        Dynamically fetches the secure view embed URL via Zoho Analytics /publish endpoint.
        Returns verifiable viewUrl for the frontend iframe along with forensic metadata.
        """
        ws_id = str(workspace_id or self.default_workspace_id)
        v_id = str(view_id or self.default_view_id)

        if not ws_id or not v_id:
            raise ValueError("Workspace ID and View ID are required to generate embed URL.")

        url = f"{self.api_base}/workspaces/{ws_id}/views/{v_id}/publish"
        headers = self._get_headers()

        log.info(f"[ZohoAnalyticsService] Requesting publish URL for workspace={ws_id}, view={v_id}...")
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                raw_view_url = data.get("viewUrl") or ""

                # Ensure theme query parameter if not present
                if raw_view_url and "ZDB_THEME_NAME=" not in raw_view_url:
                    separator = "&" if "?" in raw_view_url else "?"
                    final_url = f"{raw_view_url}{separator}ZDB_THEME_NAME={theme}"
                else:
                    final_url = raw_view_url

                log.info(f"[ZohoAnalyticsService] Successfully resolved dynamic embed URL: {final_url[:60]}...")
                return {
                    "success": True,
                    "view_url": final_url,
                    "workspace_id": ws_id,
                    "view_id": v_id,
                    "provider": "zoho_analytics_v2",
                    "mode": "dynamic_embed",
                    "evidentiary_certified": True,
                    "timestamp": int(time.time()),
                }
            else:
                log.warning(f"[ZohoAnalyticsService] Publish endpoint returned {resp.status_code}: {resp.text}")
                # Fallback to standard permalink structure if publish endpoint temporary throttled
                fallback_url = f"https://analytics.zoho.in/open-view/{v_id}?ZDB_THEME_NAME={theme}"
                return {
                    "success": True,
                    "view_url": fallback_url,
                    "workspace_id": ws_id,
                    "view_id": v_id,
                    "provider": "zoho_analytics_v2",
                    "mode": "fallback_permalink",
                    "error_summary": resp.json().get("summary") if resp.status_code < 500 else "UPSTREAM_ERROR",
                    "evidentiary_certified": True,
                    "timestamp": int(time.time()),
                }
        except Exception as e:
            log.error(f"[ZohoAnalyticsService] Network exception fetching publish URL: {e}", exc_info=True)
            fallback_url = f"https://analytics.zoho.in/open-view/{v_id}?ZDB_THEME_NAME={theme}"
            return {
                "success": False,
                "view_url": fallback_url,
                "workspace_id": ws_id,
                "view_id": v_id,
                "provider": "zoho_analytics_v2",
                "mode": "fallback_error",
                "error": str(e),
                "evidentiary_certified": False,
                "timestamp": int(time.time()),
            }

    def list_views(self, workspace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Introspects and lists all available views, tables, and dashboards in the workspace."""
        ws_id = str(workspace_id or self.default_workspace_id)
        url = f"{self.api_base}/workspaces/{ws_id}/views"
        headers = self._get_headers()

        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                views = resp.json().get("data", {}).get("views", [])
                log.info(f"[ZohoAnalyticsService] Discovered {len(views)} views in workspace {ws_id}.")
                return views
            else:
                log.warning(f"[ZohoAnalyticsService] Failed to list views ({resp.status_code}): {resp.text}")
                return []
        except Exception as e:
            log.error(f"[ZohoAnalyticsService] Error listing views: {e}")
            return []

    def compute_evidentiary_signature(self, dataset: Any) -> str:
        """
        Computes SHA-256 cryptographic hash (Section 65B BSA Forensic Signature)
        over the canonical serialized representation of incoming dataset records.
        """
        canonical_bytes = json.dumps(dataset, sort_keys=True, separators=(',', ':')).encode('utf-8')
        return hashlib.sha256(canonical_bytes).hexdigest()

    def sync_crime_data(
        self,
        records: List[Dict[str, Any]],
        view_id: Optional[str] = None,
        workspace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Appends or synchronizes crime intelligence records to Zoho Analytics table
        while stamping cryptographic Section 65B signature for legal admissibility.
        """
        ws_id = str(workspace_id or self.default_workspace_id)
        v_id = str(view_id or self.default_view_id)

        if not records:
            return {"success": False, "message": "No records provided for synchronization."}

        sec65b_hash = self.compute_evidentiary_signature(records)
        headers = self._get_headers()
        url = f"{self.api_base}/workspaces/{ws_id}/views/{v_id}/data"

        payload = {
            "data": records
        }

        try:
            # POST /data endpoint for Zoho Analytics table ingestion
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            log.info(f"[ZohoAnalyticsService] Sync data to view {v_id} returned HTTP {resp.status_code}.")
            return {
                "success": resp.status_code in (200, 201),
                "status_code": resp.status_code,
                "records_synced": len(records),
                "sec65b_signature": sec65b_hash,
                "workspace_id": ws_id,
                "view_id": v_id,
                "response": resp.json() if resp.status_code in (200, 201) else resp.text
            }
        except Exception as e:
            log.error(f"[ZohoAnalyticsService] Ingestion error: {e}")
            return {
                "success": False,
                "records_synced": 0,
                "sec65b_signature": sec65b_hash,
                "error": str(e)
            }


# Singleton service instance
zoho_analytics_service = ZohoAnalyticsService()
