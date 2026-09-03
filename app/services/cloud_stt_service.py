"""
KSP Sentinel AI — Cloud Audio Forensics & Multi-Engine STT Service (SOLID: SRP, OCP, DIP)
==========================================================================================
Architecture:
- BaseSTTProvider: Abstract Base Class defining standard provider contract (OCP/DIP).
- ZohoZiaSTTProvider: Primary Enterprise Provider communicating with Zoho Catalyst Zia Audio STT.
- GroqWhisperSTTProvider: Ultra-Fast Fallback Provider utilizing Groq Cloud Whisper-large-v3 LPU.
- CloudSTTService: Resilient Orchestrator managing Primary -> Fallback execution lifecycle (SRP).

All operations operate strictly in-memory (io.BytesIO) with zero temporary disk artifacts.
Zero hardcoding — all endpoints and credentials are bound to app.config.
"""
import io
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from app.config import (
    GROQ_API_KEY,
    ZIA_AUDIO_ENDPOINT,
    CATALYST_ORG_ID,
)
from app.services.zoho_token_manager import zoho_token_manager

log = logging.getLogger("standalone.service.cloud_stt")


class BaseSTTProvider(ABC):
    """
    Abstract Base Class for Speech-to-Text Providers (Dependency Inversion Principle).
    """
    @abstractmethod
    def transcribe(self, file_bytes: bytes, filename: str, language: str = "en") -> Dict[str, Any]:
        """
        Standardized Transcription Contract.
        Returns:
            {
                "success": bool,
                "text": str,
                "language": str,
                "processing_time_ms": float,
                "provider": str,
                "error": Optional[str]
            }
        """
        pass


class ZohoZiaSTTProvider(BaseSTTProvider):
    """
    Primary Provider: Native Zoho Catalyst Zia Speech-to-Text API with OAuth Auto-Recovery.
    """
    def __init__(self):
        self.org_id = CATALYST_ORG_ID
        self.endpoint_url = ZIA_AUDIO_ENDPOINT

    @property
    def access_token(self) -> Optional[str]:
        return zoho_token_manager.get_valid_token(purpose="zia")

    def refresh_access_token(self) -> Optional[str]:
        return zoho_token_manager.get_valid_token(purpose="zia", force_refresh=True)

    def transcribe(self, file_bytes: bytes, filename: str, language: str = "en") -> Dict[str, Any]:
        import requests

        content_type = "audio/mpeg" if filename.lower().endswith(".mp3") else "audio/wav"
        clean_ext = ".mp3" if filename.lower().endswith(".mp3") else ".wav"
        safe_zoho_filename = f"audio_recording{clean_ext}"

        t0 = time.time()
        for attempt in range(2):
            token = self.access_token
            if not token:
                log.warning("[ZohoZiaSTTProvider] No valid Zoho Zia OAuth token available.")
                token = self.refresh_access_token()
                if not token:
                    return {
                        "success": False,
                        "error": "Zoho Zia OAuth token unavailable.",
                        "provider": "zoho_zia_speech"
                    }

            headers = {
                "CATALYST-ORG": str(self.org_id),
                "Authorization": f"Zoho-oauthtoken {token}"
            }
            files = {
                "file": (safe_zoho_filename, file_bytes, content_type)
            }
            data = {"language": language}

            try:
                log.info(f"[ZohoZiaSTTProvider] Dispatching {len(file_bytes)} bytes to {self.endpoint_url} (attempt {attempt+1})")
                res = requests.post(self.endpoint_url, headers=headers, files=files, data=data, timeout=12)

                if res.status_code == 401 and attempt == 0:
                    log.warning("[ZohoZiaSTTProvider] 401 Unauthorized from Zia API. Refreshing token...")
                    self.refresh_access_token()
                    continue

                proc_ms = round((time.time() - t0) * 1000, 2)
                if res.status_code == 200:
                    res_json = res.json()
                    transcribed_text = res_json.get("text", "").strip()
                    if transcribed_text:
                        return {
                            "success": True,
                            "text": transcribed_text,
                            "language": res_json.get("language", language),
                            "processing_time_ms": res_json.get("processing_time_ms", proc_ms),
                            "provider": "zoho_zia_speech"
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Zoho Zia returned empty transcript.",
                            "provider": "zoho_zia_speech"
                        }
                else:
                    log.warning(f"[ZohoZiaSTTProvider] HTTP {res.status_code}: {res.text[:200]}")
                    return {
                        "success": False,
                        "status_code": res.status_code,
                        "error": f"Zoho Zia API error: {res.status_code}",
                        "provider": "zoho_zia_speech"
                    }
            except Exception as exc:
                log.warning(f"[ZohoZiaSTTProvider] Request exception: {exc}")
                return {
                    "success": False,
                    "error": str(exc),
                    "provider": "zoho_zia_speech"
                }

        return {
            "success": False,
            "error": "Zoho Zia STT failed after OAuth retry attempts.",
            "provider": "zoho_zia_speech"
        }


class GroqWhisperSTTProvider(BaseSTTProvider):
    """
    Fallback Provider: Groq Cloud Whisper-large-v3 LPU Inference Engine.
    Sub-400ms multilingual transcription for Kannada, Hindi, and English.
    """
    def __init__(self):
        self._api_key = GROQ_API_KEY
        self._client = None

    def _get_client(self):
        if self._client is None and self._api_key:
            try:
                from groq import Groq
                self._client = Groq(api_key=self._api_key, timeout=15.0)
            except Exception as exc:
                log.error(f"[GroqWhisperSTTProvider] Failed to initialize Groq client: {exc}")
        return self._client

    def transcribe(self, file_bytes: bytes, filename: str, language: str = "en") -> Dict[str, Any]:
        client = self._get_client()
        if not client:
            return {
                "success": False,
                "error": "Groq client not configured or missing GROQ_API_KEY.",
                "provider": "cloud_whisper_large_v3"
            }

        t0 = time.time()
        try:
            clean_name = filename if filename.endswith((".mp3", ".wav", ".ogg", ".m4a", ".flac")) else f"{filename}.mp3"
            audio_buffer = (clean_name, io.BytesIO(file_bytes))

            log.info(f"[GroqWhisperSTTProvider] Streaming {len(file_bytes)} bytes to Groq Whisper LPU...")
            
            # Map languages if needed (Groq Whisper accepts ISO-639-1 e.g. 'kn', 'hi', 'en')
            lang_param = language.lower() if language and language.lower() in ("kn", "hi", "en", "ta", "te") else None

            transcription = client.audio.transcriptions.create(
                file=audio_buffer,
                model="whisper-large-v3",
                response_format="json",
                language=lang_param,
                temperature=0.0
            )

            proc_ms = round((time.time() - t0) * 1000, 2)
            transcribed_text = getattr(transcription, "text", str(transcription)).strip()

            return {
                "success": bool(transcribed_text),
                "text": transcribed_text,
                "language": language,
                "processing_time_ms": proc_ms,
                "provider": "cloud_whisper_large_v3"
            }
        except Exception as exc:
            proc_ms = round((time.time() - t0) * 1000, 2)
            log.error(f"[GroqWhisperSTTProvider] Transcription failed ({proc_ms}ms): {exc}")
            return {
                "success": False,
                "error": str(exc),
                "processing_time_ms": proc_ms,
                "provider": "cloud_whisper_large_v3"
            }


class CloudSTTService:
    """
    Unified Audio Forensics STT Service Orchestrator (Single Responsibility & Open/Closed Principle).
    Prioritizes Zoho Zia Speech API as Primary; seamlessly fails over to Groq Whisper LPU.
    """
    def __init__(self, primary: Optional[BaseSTTProvider] = None, fallback: Optional[BaseSTTProvider] = None):
        self.primary_provider = primary or ZohoZiaSTTProvider()
        self.fallback_provider = fallback or GroqWhisperSTTProvider()

    def transcribe_audio(self, file_bytes: bytes, filename: str, language: str = "en") -> Dict[str, Any]:
        """
        Executes Primary -> Fallback Audio Transcription Pipeline.
        """
        if not file_bytes:
            return {
                "success": False,
                "error": "Empty audio buffer received.",
                "provider": "none"
            }

        # ── Step 1: Attempt Primary Provider (Zoho Zia STT) ──
        log.info(f"[CloudSTTService] Invoking Primary STT Provider: {self.primary_provider.__class__.__name__}")
        res = self.primary_provider.transcribe(file_bytes, filename, language=language)

        if res.get("success") and res.get("text"):
            log.info(f"[CloudSTTService] Primary provider succeeded in {res.get('processing_time_ms', 0)}ms ({res.get('provider')})")
            return res

        # ── Step 2: Failover to Fallback Provider (Groq Whisper-large-v3) ──
        log.warning(f"[CloudSTTService] Primary provider failed ({res.get('error')}). Engaging Fallback: {self.fallback_provider.__class__.__name__}")
        fallback_res = self.fallback_provider.transcribe(file_bytes, filename, language=language)

        if fallback_res.get("success") and fallback_res.get("text"):
            log.info(f"[CloudSTTService] Fallback provider recovered audio transcription in {fallback_res.get('processing_time_ms', 0)}ms ({fallback_res.get('provider')})")
            return fallback_res

        # ── Step 3: Both Providers Failed ──
        log.error(f"[CloudSTTService] Both Primary and Fallback STT providers failed.")
        return {
            "success": False,
            "error": f"Primary ({res.get('error')}) | Fallback ({fallback_res.get('error')})",
            "provider": "failed_all"
        }


# Global Singleton Service Instance
cloud_stt_service = CloudSTTService()
