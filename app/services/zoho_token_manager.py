"""
KSP Sentinel AI — Enterprise Multi-Token OAuth Manager (SOLID: SRP + OCP + Thread-Safe)
=======================================================================================
Provides unified, thread-safe, single-flight token management for Zoho Catalyst services
(Projects, Tables/DataStore, Cache, QuickML, Zia Speech) and Zoho Analytics.

Core Principles Adhered To:
- SOLID: SRP (OAuth Lifecycle Management), OCP (Bucket-based purpose routing),
         LSP (Consistent token retrieval contract), ISP (Focused public API), DIP (Config abstraction).
- DRY: Single-flight token refresh across all Catalyst purposes backed by unified scope.
- Anti-Desync: Automatic candidate election with typo self-healing across env variables.
- Zero Hardcoding: Reads strictly from app.config with no hardcoded credentials.
- Thread Safety: Double-checked locking with threading.RLock and proactive 8-minute TTL buffer.
"""
import logging
import threading
import time
from typing import Any, Dict, List, Optional, Set
import requests

from app.config import (
    ZOHO_ACCESS_TOKEN,
    ZOHO_REFRESH_TOKEN,
    ZOHO_CLIENT_ID,
    ZOHO_CLIENT_SECRET,
    ZOHO_REFRESH_TOKEN_PROJECTS,
    ZOHO_ACCESS_TOKEN_PROJECTS,
    ZOHO_REFRESH_TOKEN_TABLES,
    ZOHO_ACCESS_TOKEN_TABLES,
    ZOHO_REFRESH_TOKEN_CACHE,
    ZOHO_ACCESS_TOKEN_CACHE,
    ZOHO_REFRESH_TOKEN_QUICKML,
    ZOHO_ACCESS_TOKEN_QUICKML,
    ZOHO_REFRESH_TOKEN_ZIA,
    ZOHO_ACCESS_TOKEN_ZIA,
    ZOHO_REFRESH_TOKEN_ANALYTICS,
    ZOHO_ACCESS_TOKEN_ANALYTICS,
    CATALYST_PROJECT_ID,
    CATALYST_CACHE_SEGMENT_ID,
    CATALYST_API_BASE,
    CATALYST_ORG_ID,
)

log = logging.getLogger("standalone.zoho_token_manager")

# Proactive refresh buffer: Refresh 8 minutes (480s) before Zoho token expires
REFRESH_BUFFER_SECONDS = 480
DEFAULT_TOKEN_LIFETIME = 3600  # 1 hour standard Zoho access token


class ZohoTokenManager:
    """
    Thread-safe, singleton multi-token manager providing cached access tokens
    with single-flight refresh across shared-scope Catalyst services and
    dedicated lifecycle management for Zoho Analytics.
    """
    _instance = None
    _lock = threading.RLock()

    # Buckets
    CATALYST_PURPOSES: Set[str] = {"projects", "tables", "cache", "quickml", "zia"}
    ANALYTICS_PURPOSES: Set[str] = {"analytics"}
    ALL_PURPOSES = ("projects", "tables", "cache", "quickml", "zia", "analytics")

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ZohoTokenManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._client_id = (ZOHO_CLIENT_ID or "").strip()
        self._client_secret = (ZOHO_CLIENT_SECRET or "").strip()
        self._cooldown_seconds = 10  # Minimum cooldown between refresh attempts to prevent 429/400

        # Catalyst Bucket State (Shared across projects, tables, cache, quickml, zia)
        self._catalyst_access_token: str = (
            ZOHO_ACCESS_TOKEN_PROJECTS or ZOHO_ACCESS_TOKEN or ZOHO_ACCESS_TOKEN_TABLES or
            ZOHO_ACCESS_TOKEN_CACHE or ZOHO_ACCESS_TOKEN_QUICKML or ZOHO_ACCESS_TOKEN_ZIA or ""
        ).strip()
        self._catalyst_expiry_ts: float = 0.0
        self._catalyst_last_attempt: float = 0.0
        self._catalyst_refresh_lock = threading.RLock()

        # Build candidate refresh token list for Catalyst (Typo Self-Healing)
        self._catalyst_refresh_candidates: List[str] = self._build_clean_candidates([
            ZOHO_REFRESH_TOKEN_PROJECTS,
            ZOHO_REFRESH_TOKEN_TABLES,
            ZOHO_REFRESH_TOKEN_CACHE,
            ZOHO_REFRESH_TOKEN_QUICKML,
            ZOHO_REFRESH_TOKEN_ZIA,
            ZOHO_REFRESH_TOKEN,
        ])
        self._active_catalyst_refresh_token: str = (
            self._catalyst_refresh_candidates[0] if self._catalyst_refresh_candidates else ""
        )

        # Analytics Bucket State (Isolated dedicated lifecycle)
        self._analytics_access_token: str = (ZOHO_ACCESS_TOKEN_ANALYTICS or "").strip()
        self._analytics_expiry_ts: float = 0.0
        self._analytics_last_attempt: float = 0.0
        self._analytics_refresh_lock = threading.RLock()
        self._analytics_refresh_candidates: List[str] = self._build_clean_candidates([
            ZOHO_REFRESH_TOKEN_ANALYTICS,
        ])
        self._active_analytics_refresh_token: str = (
            self._analytics_refresh_candidates[0] if self._analytics_refresh_candidates else ""
        )

        self._initialized = True
        log.info(
            f"[ZohoTokenManager] Initialized with Unified Catalyst Engine. "
            f"Catalyst candidates: {len(self._catalyst_refresh_candidates)}, "
            f"Analytics candidates: {len(self._analytics_refresh_candidates)}."
        )

    @staticmethod
    def _build_clean_candidates(raw_list: List[Optional[str]]) -> List[str]:
        """Filters, cleans, and deduplicates token candidates while preserving order."""
        seen: Set[str] = set()
        cleaned: List[str] = []
        for item in raw_list:
            if not item:
                continue
            token_str = item.strip().strip("'\"")
            if token_str and token_str not in seen:
                seen.add(token_str)
                cleaned.append(token_str)
        return cleaned

    def _normalize_purpose(self, purpose: Optional[str]) -> str:
        if not purpose or purpose.lower() in ("default", "master", "general", "all"):
            return "projects"
        p = purpose.lower().strip()
        if p in ("datastore", "db", "database"):
            return "tables"
        if p in ("ml", "rag", "quickml_read"):
            return "quickml"
        if p in ("stt", "speech", "face", "mlkit"):
            return "zia"
        if p in ("analytics", "reports", "dashboard", "charts", "bi"):
            return "analytics"
        if p in self.ALL_PURPOSES:
            return p
        return "projects"

    def get_valid_token(self, purpose: str = "projects", force_refresh: bool = False) -> Optional[str]:
        """
        Retrieves a valid, proactive-refreshed access token for the requested purpose.
        Uses single-flight shared caching for all Catalyst purposes to prevent rate-limiting.
        """
        p = self._normalize_purpose(purpose)

        if p in self.ANALYTICS_PURPOSES:
            return self._get_analytics_token(force_refresh=force_refresh)
        return self._get_catalyst_token(purpose_tag=p, force_refresh=force_refresh)

    def _get_catalyst_token(self, purpose_tag: str, force_refresh: bool = False) -> Optional[str]:
        """Returns valid Catalyst access token with double-checked single-flight refresh."""
        now = time.time()

        # Fast path (cache hit without lock)
        if not force_refresh and self._catalyst_access_token and now < self._catalyst_expiry_ts:
            return self._catalyst_access_token

        with self._catalyst_refresh_lock:
            now = time.time()
            # Double check inside lock
            if not force_refresh and self._catalyst_access_token and now < self._catalyst_expiry_ts:
                return self._catalyst_access_token

            # Cooldown guard to protect from dogpiling/rate limits
            if (now - self._catalyst_last_attempt) < self._cooldown_seconds and self._catalyst_access_token:
                log.debug(f"[ZohoTokenManager] Catalyst token in cooldown buffer, returning existing token.")
                return self._catalyst_access_token

            # Execute single-flight refresh
            refreshed = self._refresh_catalyst_token(purpose_tag=purpose_tag)
            if refreshed:
                return refreshed

            return self._catalyst_access_token or None

    def _refresh_catalyst_token(self, purpose_tag: str) -> Optional[str]:
        """Executes OAuth token refresh across candidate tokens with typo self-healing."""
        self._catalyst_last_attempt = time.time()

        if not (self._client_id and self._client_secret):
            log.warning("[ZohoTokenManager] Missing client_id or client_secret for Catalyst token refresh.")
            return self._catalyst_access_token or None

        if not self._catalyst_refresh_candidates:
            log.warning("[ZohoTokenManager] No Catalyst refresh token candidates configured.")
            return self._catalyst_access_token or None

        url = "https://accounts.zoho.in/oauth/v2/token"

        # Attempt active candidate first, then cycle through backup candidates if error occurs
        for idx, candidate in enumerate(self._catalyst_refresh_candidates):
            data = {
                "refresh_token": candidate,
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "grant_type": "refresh_token",
            }
            masked_candidate = f"{candidate[:8]}...{candidate[-4:]}" if len(candidate) > 12 else candidate
            log.info(
                f"[ZohoTokenManager] [Single-Flight] Requesting Catalyst access token for [{purpose_tag}] "
                f"using candidate #{idx + 1} ({masked_candidate})..."
            )

            try:
                res = requests.post(url, data=data, timeout=8)
                if res.status_code == 200:
                    res_data = res.json()
                    new_token = res_data.get("access_token")
                    expires_in = int(res_data.get("expires_in", DEFAULT_TOKEN_LIFETIME))
                    if new_token:
                        self._catalyst_access_token = new_token
                        self._catalyst_expiry_ts = time.time() + max(120, expires_in - REFRESH_BUFFER_SECONDS)
                        self._active_catalyst_refresh_token = candidate
                        log.info(
                            f"[ZohoTokenManager] Catalyst unified token refreshed successfully! "
                            f"Valid for {expires_in}s (next refresh in {expires_in - REFRESH_BUFFER_SECONDS}s)."
                        )
                        return new_token
                else:
                    log.warning(
                        f"[ZohoTokenManager] Candidate #{idx + 1} ({masked_candidate}) failed with "
                        f"HTTP {res.status_code}: {res.text}. Trying next candidate..."
                    )
            except Exception as e:
                log.warning(f"[ZohoTokenManager] Exception refreshing with candidate #{idx + 1}: {e}")

        log.error("[ZohoTokenManager] All Catalyst refresh token candidates failed. Using fallback access token if present.")
        return self._catalyst_access_token or None

    def _get_analytics_token(self, force_refresh: bool = False) -> Optional[str]:
        """Returns valid Analytics access token with dedicated single-flight refresh."""
        now = time.time()

        if not force_refresh and self._analytics_access_token and now < self._analytics_expiry_ts:
            return self._analytics_access_token

        with self._analytics_refresh_lock:
            now = time.time()
            if not force_refresh and self._analytics_access_token and now < self._analytics_expiry_ts:
                return self._analytics_access_token

            if (now - self._analytics_last_attempt) < self._cooldown_seconds and self._analytics_access_token:
                return self._analytics_access_token

            refreshed = self._refresh_analytics_token()
            if refreshed:
                return refreshed

            return self._analytics_access_token or None

    def _refresh_analytics_token(self) -> Optional[str]:
        """Executes OAuth token refresh for Zoho Analytics scope."""
        self._analytics_last_attempt = time.time()

        if not (self._client_id and self._client_secret):
            return self._analytics_access_token or None

        if not self._analytics_refresh_candidates:
            log.warning("[ZohoTokenManager] No Analytics refresh token configured.")
            return self._analytics_access_token or None

        url = "https://accounts.zoho.in/oauth/v2/token"
        for candidate in self._analytics_refresh_candidates:
            data = {
                "refresh_token": candidate,
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "grant_type": "refresh_token",
            }
            try:
                res = requests.post(url, data=data, timeout=8)
                if res.status_code == 200:
                    res_data = res.json()
                    new_token = res_data.get("access_token")
                    expires_in = int(res_data.get("expires_in", DEFAULT_TOKEN_LIFETIME))
                    if new_token:
                        self._analytics_access_token = new_token
                        self._analytics_expiry_ts = time.time() + max(120, expires_in - REFRESH_BUFFER_SECONDS)
                        self._active_analytics_refresh_token = candidate
                        log.info(f"[ZohoTokenManager] Analytics token refreshed successfully! Valid for {expires_in}s.")
                        return new_token
                else:
                    log.warning(f"[ZohoTokenManager] Analytics token refresh failed HTTP {res.status_code}: {res.text}")
            except Exception as e:
                log.warning(f"[ZohoTokenManager] Analytics token refresh exception: {e}")

        return self._analytics_access_token or None

    def get_status(self) -> Dict[str, Any]:
        """Returns diagnostic status of all purpose tokens with masked previews."""
        now = time.time()
        status: Dict[str, Any] = {}
        with self._lock:
            # Catalyst status
            cat_tok = self._catalyst_access_token or ""
            cat_ref = self._active_catalyst_refresh_token or ""
            cat_ttl = max(0, int(self._catalyst_expiry_ts - now)) if cat_tok else 0
            cat_info = {
                "has_access_token": bool(cat_tok),
                "access_token_preview": f"{cat_tok[:10]}...{cat_tok[-4:]}" if len(cat_tok) > 14 else (cat_tok if cat_tok else "None"),
                "has_refresh_token": bool(cat_ref),
                "refresh_token_preview": f"{cat_ref[:10]}...{cat_ref[-4:]}" if len(cat_ref) > 14 else (cat_ref if cat_ref else "None"),
                "ttl_seconds_remaining": cat_ttl,
                "is_active": bool(cat_tok) and (cat_ttl > 0 or not bool(cat_ref)),
                "engine": "unified_single_flight",
                "candidates_count": len(self._catalyst_refresh_candidates),
            }

            for p in self.CATALYST_PURPOSES:
                status[p] = dict(cat_info)

            # Analytics status
            ana_tok = self._analytics_access_token or ""
            ana_ref = self._active_analytics_refresh_token or ""
            ana_ttl = max(0, int(self._analytics_expiry_ts - now)) if ana_tok else 0
            status["analytics"] = {
                "has_access_token": bool(ana_tok),
                "access_token_preview": f"{ana_tok[:10]}...{ana_tok[-4:]}" if len(ana_tok) > 14 else (ana_tok if ana_tok else "None"),
                "has_refresh_token": bool(ana_ref),
                "refresh_token_preview": f"{ana_ref[:10]}...{ana_ref[-4:]}" if len(ana_ref) > 14 else (ana_ref if ana_ref else "None"),
                "ttl_seconds_remaining": ana_ttl,
                "is_active": bool(ana_tok) and (ana_ttl > 0 or not bool(ana_ref)),
                "engine": "isolated_dedicated",
                "candidates_count": len(self._analytics_refresh_candidates),
            }

        return status


# Singleton instance
zoho_token_manager = ZohoTokenManager()
