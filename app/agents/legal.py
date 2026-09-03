"""
KSP Sentinel AI — Legal Knowledge Base Agent (SOLID: SRP + LSP + DIP)
====================================================================
The Immutable Global Base Agent:
- Bound to the 52 Statutory Law and Procedural Documents in Zoho Catalyst Cloud RAG.
- Persists globally across all user sessions.
- Enforces strict purpose-driven police guardrails: rejects off-topic queries (vacations, recipes, etc.).
- Covers Bharatiya Nyaya Sanhita (BNS), BNSS, Bharatiya Sakshya Adhiniyam (BSA), IPC, CrPC, IT Act & SOPs.
"""
import logging
from typing import List, Optional

from app.config import KSP_LEGAL_KNOWLEDGE_PROMPT
from app.core.interfaces import AgentManifest, AgentResponse, BaseAgent, ExecutionContext
from app.providers.orchestrator import llm_complete

log = logging.getLogger("standalone.agents.legal")


class LegalKnowledgeAgent(BaseAgent):
    """
    SRP: Authoritative statutory law, legal mappings, and standard operating procedures.
    DIP: Injects neural reasoning provider via llm_complete orchestrator.
    LSP: Returns standardized AgentResponse contract.
    """

    @property
    def manifest(self) -> AgentManifest:
        return AgentManifest(
            intent_name="LEGAL_KNOWLEDGE",
            label="Legal Knowledge Base",
            icon="⚖️",
            color="#059669",
            description="Authoritative statutory law advisor for Bharatiya Nyaya Sanhita (BNS), BNSS, BSA 2023, IPC, CrPC, IT Act, and KSP Standard Operating Procedures.",
            requires_visual_studio=False,
            system_prompt=KSP_LEGAL_KNOWLEDGE_PROMPT,
            trigger_examples=[
                "What is the punishment under Section 303(2) BNS?",
                "What are the mandatory Section 65B electronic certificate requirements?",
                "Explain the zero FIR registration procedure under BNSS."
            ],
            required_provider_tags=["rag_document", "free_reasoning"]
        )

    def execute(self, ctx: ExecutionContext) -> AgentResponse:
        messages = [
            {"role": "system", "content": self.manifest.system_prompt}
        ]

        # Dialogue History preview
        for h in ctx.history[-6:]:
            if isinstance(h, dict) and h.get("role") in ("user", "assistant") and h.get("content"):
                messages.append({"role": h["role"], "content": h["content"]})

        messages.append({"role": "user", "content": ctx.query})

        # Neural LLM Completion (Zoho QuickML / Groq / Gemini)
        answer, provider = llm_complete(
            messages,
            json_mode=False,
            max_tokens=750,
            required_tags=self.manifest.required_provider_tags
        )

        manifest = self.manifest
        suggested_actions = [
            "Check Section 65B BSA Certificate Rules",
            "View BNS vs IPC Statutory Cross-Mapping",
            "Review Mandatory Videography SOP under Sec 105 BNSS"
        ]

        return AgentResponse(
            answer=answer,
            agent_type="legal_knowledge_agent",
            agent_label=manifest.label,
            agent_icon=manifest.icon,
            agent_color=manifest.color,
            charts=[],
            executive_decision=None,
            provider=provider,
            visuals_updated=False,
            data_available=True,
            suggested_actions=suggested_actions
        )
