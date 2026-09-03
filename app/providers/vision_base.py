"""
KSP Sentinel AI — Multimodal Vision-Language Provider Abstract Interface (SOLID: DIP)
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


class BaseVLMProvider(ABC):
    """
    DIP / OCP: Abstract base contract for all multimodal vision-language inference providers.
    Allows vision models (e.g. Zoho Catalyst QuickML Qwen VLM, local vision models) to be
    plugged in without altering core forensic or agent routing pipelines.
    """
    name: str = "base_vlm"
    tags: List[str] = ["vision_enabled"]

    @abstractmethod
    def complete_vision(
        self,
        prompt: str,
        images: List[str],
        system_prompt: str = "Be concise and factual.",
        json_mode: bool = False,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_k: int = 50,
        top_p: float = 0.9,
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Executes vision-language completion over provided prompt and base64/URL images.
        Returns:
            Tuple of (response_text, provider_name, metrics_dict)
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Returns whether this VLM provider has necessary credentials and endpoints configured."""
        pass
