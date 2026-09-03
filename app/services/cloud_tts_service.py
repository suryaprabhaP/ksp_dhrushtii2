"""
KSP Sentinel AI — Cloud Audio Synthesis & Multi-Engine TTS Service (SOLID: SRP, OCP, DIP)
==========================================================================================
Architecture:
- BaseTTSProvider: Abstract Base Class defining standard synthesis contract (OCP/DIP).
- ZohoZiaTTSProvider: Primary Enterprise Provider communicating with Zoho Catalyst Zia TTS API.
- CloudTTSService: Orchestrator managing Language/Speaker normalization and Base64 formatting (SRP).

All operations operate in-memory with zero temporary disk artifacts.
Zero hardcoding — all endpoints and credentials are bound to app.config and zoho_token_manager.
"""
import base64
import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

import requests

from app.config import (
    ZIA_TTS_ENDPOINT,
    CATALYST_ORG_ID,
)
from app.services.zoho_token_manager import zoho_token_manager

log = logging.getLogger("standalone.service.cloud_tts")

# Standard Speaker Mappings across Supported Indic & English Languages
DEFAULT_SPEAKERS = {
    "en": "Mary",      # Options: Thomas, Adam, Brian, Mary, Anna, Beth
    "hi": "Divya",     # Options: Rohit, Aman, Divya, Rani
    "kn": "Anu",       # Options: Suresh, Chetan, Anu, Vidya
}

SUPPORTED_LANGUAGES = {"en", "hi", "kn"}
DEFAULT_PITCH = "moderate"
DEFAULT_SPEED = "moderate"
DEFAULT_EMOTION = "neutral"


class BaseTTSProvider(ABC):
    """
    Abstract Base Class for Text-to-Speech Synthesis Providers (Dependency Inversion Principle).
    """
    @abstractmethod
    def synthesize(
        self,
        text: str,
        language: str = "en",
        speaker: Optional[str] = None,
        pitch: str = DEFAULT_PITCH,
        speed: str = DEFAULT_SPEED,
        emotion: str = DEFAULT_EMOTION
    ) -> Dict[str, Any]:
        """
        Standardized Synthesis Contract.
        Returns:
            {
                "success": bool,
                "audio_bytes": bytes,
                "audio_b64": str,
                "provider": str,
                "processing_time_ms": float,
                "audio_info": Dict[str, Any],
                "error": Optional[str]
            }
        """
        pass


class ZohoZiaTTSProvider(BaseTTSProvider):
    """
    Primary Provider: Native Zoho Catalyst Zia Text-to-Audio Synthesis API with OAuth Auto-Recovery.
    Endpoint: https://api.catalyst.zoho.in/quickml/api/v1/models/zia/tts/synthesize
    """
    def __init__(self):
        self.org_id = CATALYST_ORG_ID
        self.endpoint_url = ZIA_TTS_ENDPOINT

    @property
    def access_token(self) -> Optional[str]:
        return zoho_token_manager.get_valid_token(purpose="quickml")

    def refresh_access_token(self) -> Optional[str]:
        return zoho_token_manager.get_valid_token(purpose="quickml", force_refresh=True)

    def synthesize(
        self,
        text: str,
        language: str = "en",
        speaker: Optional[str] = None,
        pitch: str = DEFAULT_PITCH,
        speed: str = DEFAULT_SPEED,
        emotion: str = DEFAULT_EMOTION
    ) -> Dict[str, Any]:
        if not text or not text.strip():
            return {
                "success": False,
                "error": "Empty text provided for synthesis.",
                "provider": "zoho_zia_tts"
            }

        resolved_speaker = speaker or DEFAULT_SPEAKERS.get(language, "Mary")

        payload = {
            "text": text.strip(),
            "language": language,
            "speaker": resolved_speaker,
            "pitch": pitch,
            "speed": speed,
            "emotion": emotion
        }

        t0 = time.time()
        for attempt in range(2):
            token = self.access_token
            if not token:
                log.warning("[ZohoZiaTTSProvider] No valid Zoho OAuth token available. Attempting refresh...")
                token = self.refresh_access_token()
                if not token:
                    return {
                        "success": False,
                        "error": "Zoho OAuth token unavailable for TTS.",
                        "provider": "zoho_zia_tts"
                    }

            headers = {
                "CATALYST-ORG": str(self.org_id),
                "Authorization": f"Zoho-oauthtoken {token}",
                "Content-Type": "application/json"
            }

            try:
                log.info(f"[ZohoZiaTTSProvider] Dispatching {len(text)} chars ({language}/{resolved_speaker}) to {self.endpoint_url} (attempt {attempt+1})")
                res = requests.post(self.endpoint_url, headers=headers, json=payload, timeout=15)

                if res.status_code == 401 and attempt == 0:
                    log.warning("[ZohoZiaTTSProvider] 401 Unauthorized from Zia TTS. Refreshing token...")
                    self.refresh_access_token()
                    continue

                proc_ms = round((time.time() - t0) * 1000, 2)

                if res.status_code == 200:
                    audio_bytes = res.content
                    if not audio_bytes:
                        return {
                            "success": False,
                            "error": "Zoho Zia TTS returned empty audio payload.",
                            "provider": "zoho_zia_tts"
                        }

                    # Parse X-Audio-Info header if present
                    audio_info_raw = res.headers.get("X-Audio-Info") or res.headers.get("x-audio-info")
                    audio_info = {}
                    if audio_info_raw:
                        try:
                            audio_info = json.loads(audio_info_raw)
                        except Exception:
                            audio_info = {"raw": audio_info_raw}

                    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                    log.info(f"[ZohoZiaTTSProvider] Successfully synthesized {len(audio_bytes)} bytes in {proc_ms}ms ({language}/{resolved_speaker})")

                    return {
                        "success": True,
                        "audio_bytes": audio_bytes,
                        "audio_b64": audio_b64,
                        "language": language,
                        "speaker": resolved_speaker,
                        "processing_time_ms": proc_ms,
                        "audio_info": audio_info,
                        "provider": "zoho_zia_tts"
                    }
                else:
                    log.warning(f"[ZohoZiaTTSProvider] HTTP {res.status_code}: {res.text[:250]}")
                    return {
                        "success": False,
                        "status_code": res.status_code,
                        "error": f"Zoho Zia TTS error: {res.status_code} - {res.text[:200]}",
                        "provider": "zoho_zia_tts"
                    }
            except Exception as exc:
                log.error(f"[ZohoZiaTTSProvider] Request exception: {exc}")
                return {
                    "success": False,
                    "error": str(exc),
                    "provider": "zoho_zia_tts"
                }

        return {
            "success": False,
            "error": "Zoho Zia TTS failed after OAuth retry attempts.",
            "provider": "zoho_zia_tts"
        }


class CloudTTSService:
    """
    Unified Audio Speech Synthesis Service Orchestrator (Single Responsibility & Open/Closed Principle).
    Prioritizes Zoho Zia Text-to-Audio Synthesis as strict Primary Engine.
    """
    def __init__(self, primary: Optional[BaseTTSProvider] = None):
        self.primary_provider = primary or ZohoZiaTTSProvider()

    def normalize_language_code(self, raw_lang: Optional[str]) -> str:
        """
        Normalizes Indic/English language tags (e.g., 'en-IN', 'hi-IN', 'kn-IN', 'kannada') to Zoho 2-letter codes.
        """
        if not raw_lang:
            return "en"
        clean = raw_lang.lower().replace("_", "-").strip()
        if clean.startswith("hi"):
            return "hi"
        if clean.startswith("kn") or "kannada" in clean:
            return "kn"
        return "en"

    def synthesize_speech(
        self,
        text: str,
        language_code: str = "en-IN",
        speaker: Optional[str] = None,
        pitch: str = DEFAULT_PITCH,
        speed: str = DEFAULT_SPEED,
        emotion: str = DEFAULT_EMOTION
    ) -> Dict[str, Any]:
        """
        Synthesizes text into high-fidelity Indic/English speech audio using the Primary Zoho Zia Engine.
        """
        if not text or not text.strip():
            return {
                "success": False,
                "error": "No text provided for speech synthesis.",
                "provider": "none"
            }

        lang = self.normalize_language_code(language_code)
        log.info(f"[CloudTTSService] Invoking Primary TTS Provider: {self.primary_provider.__class__.__name__} (Lang: {lang})")

        res = self.primary_provider.synthesize(
            text=text,
            language=lang,
            speaker=speaker,
            pitch=pitch,
            speed=speed,
            emotion=emotion
        )

        return res


# Global Singleton Service Instance
cloud_tts_service = CloudTTSService()
