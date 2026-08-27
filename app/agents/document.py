"""
KSP Sentinel AI — Document Agent (SOLID: SRP + LSP)
"""
from app.config import KSP_DOCUMENT_PROMPT
from app.core.interfaces import AgentManifest, AgentResponse, BaseAgent, ExecutionContext
from app.providers.orchestrator import llm_complete


class DocumentAgent(BaseAgent):
    """
    SRP: Handles legal section, statutory law (BNS/BNSS/BSA), SOPs, and procedural investigations.
    Output: Structured legal analysis with relevant citations.
    """
    @property
    def manifest(self) -> AgentManifest:
        return AgentManifest(
            intent_name="DOCUMENT",
            label="Document Agent",
            icon="📄",
            color="#10b981",
            description="Trigger for legal sections (IPC, BNS, BNSS, BSA, IT Act, CrPC), FIR filing procedures, Section 65B certification, or statutory police SOPs.",
            requires_visual_studio=False,
            system_prompt=KSP_DOCUMENT_PROMPT
        )

    def execute(self, ctx: ExecutionContext) -> AgentResponse:
        messages = [
            {"role": "system", "content": self.manifest.system_prompt}
        ]
        for h in ctx.history[-4:]:
            if h.get("role") in ("user", "assistant") and h.get("content"):
                messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": ctx.query})

        answer, provider = llm_complete(messages, json_mode=False, max_tokens=500)
        manifest = self.manifest

        return AgentResponse(
            answer=answer,
            agent_type="document_agent",
            agent_label=manifest.label,
            agent_icon=manifest.icon,
            agent_color=manifest.color,
            charts=[],
            executive_decision=None,
            provider=provider,
            visuals_updated=False
        )
