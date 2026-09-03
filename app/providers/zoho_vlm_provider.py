"""
KSP Sentinel AI — Zoho Catalyst QuickML Vision-Language Provider (VL-Qwen3.6-35B-A3B)
SOLID: DIP Compliant BaseVLMProvider Implementation
"""
import logging
import time
from typing import Any, Dict, List, Optional, Tuple
import requests

from app.config import (
    CATALYST_ORG_ID,
    CATALYST_PROJECT_ID,
    CATALYST_VLM_ENDPOINT,
    CATALYST_VLM_MODEL,
)
from app.providers.vision_base import BaseVLMProvider
from app.services.zoho_token_manager import zoho_token_manager

log = logging.getLogger("standalone.provider.zoho_vlm")


class ZohoQuickMLVLMProvider(BaseVLMProvider):
    """
    DIP / OCP: Official Zoho Catalyst QuickML Multimodal VLM Provider.
    Harnesses the 35B Parameter (3B Active MoE) VL-Qwen3.6-35B-A3B foundation vision model
    for CCTV intelligence, crime scene reconstruction, and multilingual OCR document parsing.
    """
    name = "zoho_quickml_vlm"
    tags = ["vision_enabled", "deep_reasoning", "thinking_preservation", "ocr_capable"]

    def __init__(self):
        self.project_id = CATALYST_PROJECT_ID
        self.org_id = CATALYST_ORG_ID
        self.endpoint_url = CATALYST_VLM_ENDPOINT
        self.primary_model = CATALYST_VLM_MODEL

    @property
    def access_token(self) -> Optional[str]:
        return zoho_token_manager.get_valid_token(purpose="quickml")

    def is_available(self) -> bool:
        return bool(self.access_token and self.project_id)

    def refresh_access_token(self) -> Optional[str]:
        return zoho_token_manager.get_valid_token(purpose="quickml", force_refresh=True)

    def complete_vision(
        self,
        prompt: str,
        images: List[str],
        system_prompt: str = "Be concise and factual.",
        json_mode: bool = False,
        max_tokens: int = 1500,
        temperature: float = 0.7,
        top_k: int = 50,
        top_p: float = 0.9,
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Executes multimodal completion over input images and analytical prompt.
        Args:
            prompt: Text instruction or forensic extraction query.
            images: List of up to 3 base64-encoded image strings.
            system_prompt: Guiding system persona / instructions.
            json_mode: When True, adds strict JSON schema guidance.
            max_tokens: Maximum generated response tokens (up to 3000).
            temperature: Sampling temperature.
            top_k: Sampling top-k candidates.
            top_p: Nucleus sampling probability.
        Returns:
            (response_text, provider_name, metrics_dict)
        """
        if not self.is_available():
            raise RuntimeError("ZohoQuickMLVLMProvider is not configured or unavailable")

        if not images:
            raise ValueError("VLM Provider requires at least 1 image payload")

        # Guardrail: Maximum 3 images per request to prevent token overflow
        sanitized_images = images[:3]

        headers = {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "CATALYST-ORG": str(self.org_id),
            "Content-Type": "application/json"
        }

        # Build prompt with JSON directive if json_mode requested
        effective_prompt = prompt
        if json_mode and "json" not in prompt.lower():
            effective_prompt = f"{prompt}\nProvide the results strictly in valid JSON format."

        body = {
            "model": self.primary_model,
            "prompt": effective_prompt,
            "images": sanitized_images,
            "system_prompt": system_prompt or "Be concise, factual, and law enforcement compliant.",
            "top_k": top_k,
            "top_p": top_p,
            "temperature": temperature if not json_mode else 0.2,
            "max_tokens": min(max_tokens, 3000)
        }

        # Attempt call with token auto-refresh retry on 401
        for attempt in range(2):
            try:
                t0 = time.time()
                log.info(f"[ZohoQuickMLVLMProvider] Dispatching multimodal request to Catalyst VLM ({self.primary_model}, {len(sanitized_images)} image(s))...")
                res = requests.post(self.endpoint_url, headers=headers, json=body, timeout=45)

                if res.status_code == 401 and attempt == 0:
                    log.info("[ZohoQuickMLVLMProvider] 401 Unauthorized received. Refreshing OAuth token...")
                    new_token = self.refresh_access_token()
                    if new_token:
                        headers["Authorization"] = f"Zoho-oauthtoken {new_token}"
                        continue

                if res.status_code == 200:
                    data = res.json()
                    response_text = data.get("response", "")
                    metrics = data.get("metrics", {})
                    metrics["request_id"] = data.get("request_id", "")
                    metrics["total_roundtrip_ms"] = round((time.time() - t0) * 1000, 2)

                    if response_text:
                        return response_text, self.name, metrics

                # If non-200 or empty, raise with snippet
                raise RuntimeError(f"Zoho QuickML VLM returned status {res.status_code}: {res.text[:300]}")

            except Exception as e:
                if attempt == 1:
                    raise e
                log.warning(f"[ZohoQuickMLVLMProvider] Attempt {attempt+1} failed: {e}")

        raise RuntimeError("Zoho QuickML VL-Qwen3.6-35B-A3B completion failed after retry")
