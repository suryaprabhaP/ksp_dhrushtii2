"""
KSP Sentinel AI — Vision Forensics & Multimodal Intelligence Agent (SOLID: SRP + DIP)
=====================================================================================
Harnesses the 35B Parameter (3B Active MoE) VL-Qwen3.6-35B-A3B foundation vision model:
1. CCTV & Suspect/Vehicle Recognition: Forensic scene reconstruction, suspect traits, vehicle tracking.
2. Bilingual Document/FIR OCR: Scanned Kannada & English FIR copies, petitions, and ID cards into structured JSON.
3. Physical Evidence Analysis: Weapon detection, points of forced entry, Sec 105 BNSS scene documentation.
"""
import json
import logging
import time
from typing import Any, Dict, List, Optional

from app.config import KSP_VISION_FORENSICS_PROMPT, KSP_VISION_OCR_PROMPT
from app.providers.orchestrator import vlm_complete

log = logging.getLogger("standalone.agent.vision")


class VisionForensicsAgent:
    """
    SRP: Dedicated domain agent for all visual and multimodal forensic intelligence tasks.
    DIP: Interacts exclusively through the abstract vlm_complete orchestrator contract.
    """
    def __init__(self):
        self.agent_type = "vision_forensics"
        self.agent_label = "Multimodal Vision & Forensics Specialist"
        self.agent_icon = "Eye"
        self.agent_color = "#3B82F6"

    def analyze_evidence(
        self,
        images: List[str],
        query: str = "",
        task_type: str = "forensics",  # "forensics", "ocr", "cctv", "auto"
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes multimodal forensic analysis over provided images and prompt.
        Args:
            images: List of base64-encoded image strings (1 to 3 images).
            query: Custom officer instructions or queries.
            task_type: Task mode ('forensics' for scene/CCTV analysis, 'ocr' for FIR/document extraction).
            session_id: Active operational session ID.
        Returns:
            Structured dictionary containing response, parsed entities, metrics, and metadata.
        """
        t0 = time.time()
        if not images:
            return {
                "success": False,
                "error": "No image payload provided for vision analysis.",
                "processing_time_ms": 0
            }

        # Determine prompt & system instruction based on task_type
        effective_task = task_type.lower()
        if effective_task in ("ocr", "document", "fir", "identity"):
            system_prompt = KSP_VISION_OCR_PROMPT
            default_prompt = "Extract all fields from the document image into structured JSON format."
            json_mode = True
        else:
            system_prompt = KSP_VISION_FORENSICS_PROMPT
            default_prompt = "Perform a thorough law enforcement forensic scene reconstruction on the provided visual evidence."
            json_mode = False

        effective_prompt = query.strip() if query and query.strip() else default_prompt

        try:
            log.info(f"[VisionForensicsAgent] Invoking VLM for task '{effective_task}' with {len(images)} image(s)...")
            content, provider_name, metrics = vlm_complete(
                prompt=effective_prompt,
                images=images,
                system_prompt=system_prompt,
                json_mode=json_mode,
                max_tokens=2000,
                temperature=0.4 if json_mode else 0.7
            )

            parsed_json = None
            if json_mode or "```json" in content:
                try:
                    # Clean markdown codeblocks if present
                    clean_str = content
                    if "```json" in clean_str:
                        clean_str = clean_str.split("```json")[1].split("```")[0].strip()
                    elif "```" in clean_str:
                        clean_str = clean_str.split("```")[1].split("```")[0].strip()
                    parsed_json = json.loads(clean_str)
                except Exception as parse_err:
                    log.warning(f"[VisionForensicsAgent] JSON parsing warning: {parse_err}")

            elapsed_ms = round((time.time() - t0) * 1000, 2)

            return {
                "success": True,
                "agent_type": self.agent_type,
                "agent_label": self.agent_label,
                "task_type": effective_task,
                "provider": provider_name,
                "raw_response": content,
                "parsed_data": parsed_json,
                "metrics": metrics,
                "image_count": len(images),
                "processing_time_ms": elapsed_ms,
                "session_id": session_id or "default_session"
            }

        except Exception as e:
            log.error(f"[VisionForensicsAgent] Multimodal analysis failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "agent_type": self.agent_type,
                "provider": "error",
                "processing_time_ms": round((time.time() - t0) * 1000, 2)
            }


# Singleton Vision Forensics Agent
vision_agent = VisionForensicsAgent()
