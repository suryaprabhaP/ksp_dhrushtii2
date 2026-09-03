"""
KSP Sentinel AI — Zoho Catalyst QuickML & GenAI Provider (Primary)
SOLID: DIP Compliant BaseLLMProvider Implementation
"""
import logging
import os
import requests
from typing import Dict, List, Optional, Tuple
from app.config import (
    CATALYST_GLM_ENDPOINT,
    CATALYST_GLM_MODEL,
    CATALYST_ORG_ID,
    CATALYST_PROJECT_ID,
    ZOHO_ACCESS_TOKEN,
    ZOHO_CLIENT_ID,
    ZOHO_CLIENT_SECRET,
    ZOHO_REFRESH_TOKEN,
)
from app.providers.base import BaseLLMProvider

from app.services.zoho_token_manager import zoho_token_manager

log = logging.getLogger("standalone.provider.zoho")

# Default 51 Indexed Knowledge Base Document IDs from Zoho Catalyst Knowledge Store
_DEFAULT_KNOWLEDGE_DOCS = [
    "3407000000004223", "3407000000003546", "3407000000004461", "3407000000004473",
    "3407000000004469", "3407000000004465", "3407000000003542", "3407000000003527",
    "3407000000003502", "3407000000004439", "3407000000003512", "3407000000003506",
    "3407000000003507", "3407000000003520", "3407000000003500", "3407000000003486",
    "3407000000003483", "3407000000003476", "3407000000004391", "3407000000003470",
    "3407000000003464", "3407000000003462", "3407000000003458", "3407000000003444",
    "3407000000003451", "3407000000003445", "3407000000003446", "3407000000004377",
    "3407000000003422", "3407000000004365", "3407000000003417", "3407000000003414",
    "3407000000004361", "3407000000003410", "3407000000004369", "3407000000003405",
    "3407000000003399", "3407000000003397", "3407000000004339", "3407000000003382",
    "3407000000004335", "3407000000003355", "3407000000004320", "3407000000004300",
    "3407000000003363", "3407000000003346", "3407000000004315", "3407000000004308",
    "3407000000004304", "3407000000003343", "3407000000003351"
]

def get_knowledge_doc_ids() -> List[str]:
    """Dynamically loads knowledge doc IDs from environment or default catalogue."""
    env_docs = os.getenv("ZOHO_KNOWLEDGE_DOCS", "")
    if env_docs:
        return [d.strip() for d in env_docs.split(",") if d.strip()]
    return list(_DEFAULT_KNOWLEDGE_DOCS)

ZOHO_KNOWLEDGE_DOCS = get_knowledge_doc_ids()


class ZohoQuickMLProvider(BaseLLMProvider):
    name = "zoho_quickml"
    tags = ["free_reasoning", "rag_document", "fast_reasoning", "long_context", "agent_workflow"]

    def __init__(self):
        self.project_id = CATALYST_PROJECT_ID
        self.org_id = CATALYST_ORG_ID
        # Official Zoho Catalyst QuickML GLM 4.7 Foundation Model Endpoint
        self.endpoint_url = CATALYST_GLM_ENDPOINT
        self.primary_model = CATALYST_GLM_MODEL

    @property
    def access_token(self) -> Optional[str]:
        return zoho_token_manager.get_valid_token(purpose="quickml")

    def is_available(self) -> bool:
        return bool(self.access_token and self.project_id)

    def refresh_access_token(self) -> Optional[str]:
        return zoho_token_manager.get_valid_token(purpose="quickml", force_refresh=True)

    def complete(self, messages: List[Dict[str, str]], json_mode: bool = False, max_tokens: int = 2500, timeout: Optional[float] = None) -> Tuple[str, str]:
        if not self.is_available():
            raise RuntimeError("ZohoQuickMLProvider is not configured or unavailable")

        headers = {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "CATALYST-ORG": str(self.org_id),
            "Content-Type": "application/json"
        }

        # Format messages according to the official Catalyst GLM OpenAI-compatible contract
        formatted_messages = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            formatted_messages.append({"role": role, "content": content})

        body = {
            "model": self.primary_model,
            "messages": formatted_messages,
            "max_tokens": min(max_tokens, 1500),
            "temperature": 0.2 if json_mode else 0.4,
            "stream": False,
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        }

        req_timeout = max(0.01, timeout) if timeout is not None else 25.0

        # Attempt call with token auto-refresh retry strictly on 401 Unauthorized
        for attempt in range(2):
            try:
                log.info(f"[ZohoQuickMLProvider] Dispatching request to Catalyst GLM 4.7 ({self.primary_model}) timeout={req_timeout}s...")
                res = requests.post(self.endpoint_url, headers=headers, json=body, timeout=req_timeout)
                
                if res.status_code == 401 and attempt == 0:
                    log.info("[ZohoQuickMLProvider] 401 Unauthorized received. Refreshing OAuth token...")
                    new_token = self.refresh_access_token()
                    if new_token:
                        headers["Authorization"] = f"Zoho-oauthtoken {new_token}"
                        continue

                if res.status_code == 200:
                    data = res.json()
                    # 1. Parse standard OpenAI-like choices format
                    if "choices" in data and data["choices"]:
                        choice_msg = data["choices"][0].get("message", {})
                        content = choice_msg.get("content") or choice_msg.get("reasoning") or ""
                        if content:
                            return content, self.name
                            
                    # 2. Parse direct response field format
                    response_text = data.get("response", "")
                    if response_text:
                        return response_text, self.name

                raise RuntimeError(f"Zoho QuickML returned status {res.status_code}: {res.text[:200]}")

            except (requests.Timeout, requests.exceptions.ReadTimeout) as e:
                log.warning(f"[ZohoQuickMLProvider] Read timeout ({req_timeout}s) exceeded: {e}")
                raise e
            except Exception as e:
                if attempt == 1:
                    raise e
                log.warning(f"[ZohoQuickMLProvider] Attempt {attempt+1} failed: {e}")

        raise RuntimeError("Zoho QuickML GLM 4.7 completion failed after retry")
