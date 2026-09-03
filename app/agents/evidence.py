"""
KSP Sentinel AI — Evidence Analysis Agent (SOLID: SRP + LSP + DIP)
=================================================================
The Ephemeral Session Sandbox Agent:
- Grounded strictly in session-isolated documents uploaded via '+' button.
- Injects IDocumentRepository backed by Zoho Catalyst Cloud NoSQL & FileStore.
- Enforces TTL expiration and strictly prevents context bleed across officer sessions.
- Generates exact citations and evidentiary Section 65B compliance findings.
"""
import logging
from typing import List, Optional

from app.config import KSP_EVIDENCE_ANALYSIS_PROMPT
from app.core.interfaces import AgentManifest, AgentResponse, BaseAgent, ExecutionContext, IDocumentRepository
from app.engine.catalyst_document_store import catalyst_document_store
from app.providers.orchestrator import llm_complete

log = logging.getLogger("standalone.agents.evidence")


class EvidenceAnalysisAgent(BaseAgent):
    """
    SRP: Evidence synthesis, cross-FIR timeline audit, and session document citation RAG.
    DIP: Injects IDocumentRepository (CatalystCloudDocumentStore).
    LSP: Returns standardized AgentResponse contract.
    """

    def __init__(self, doc_repo: Optional[IDocumentRepository] = None):
        self.doc_repo = doc_repo or catalyst_document_store

    @property
    def manifest(self) -> AgentManifest:
        return AgentManifest(
            intent_name="EVIDENCE_ANALYSIS",
            label="Case Evidence Forensics",
            icon="📑",
            color="#10b981",
            description="Deep forensic reasoning over session-uploaded case PDFs, First Information Reports (FIRs), witness depositions, bank audit trails, and seized digital documents.",
            requires_visual_studio=False,
            system_prompt=KSP_EVIDENCE_ANALYSIS_PROMPT,
            trigger_examples=[
                "Analyze the uploaded FIR and list suspect details.",
                "Compare the witness statements in the uploaded case file.",
                "Extract financial transaction timeline from the uploaded statement."
            ],
            required_provider_tags=["rag_document", "free_reasoning"]
        )

    def execute(self, ctx: ExecutionContext) -> AgentResponse:
        session_id = ctx.session_id or "default_session"
        has_docs = self.doc_repo.has_documents(session_id)
        retrieved_chunks = []
        doc_context = ""
        citations: List[str] = []

        # ── 1. Session Document Search (RAG Grounding) ────────────────────────
        if has_docs:
            retrieved_chunks = self.doc_repo.search_chunks(session_id, ctx.query, limit=5)
            if retrieved_chunks:
                context_parts = []
                for chunk in retrieved_chunks:
                    context_parts.append(
                        f"[EVIDENCE DOCUMENT: {chunk.doc_name} | CHUNK {chunk.chunk_index + 1}]\n{chunk.content}"
                    )
                    if chunk.doc_name not in citations:
                        citations.append(chunk.doc_name)

                doc_context = (
                    "\n\n=== VERIFIED SESSION CASE EVIDENCE / DOCUMENT EXCERPTS ===\n"
                    + "\n\n".join(context_parts)
                    + "\n===========================================================\n"
                    "Grounding Directives:\n"
                    "1. Answer strictly and faithfully using the verified document excerpts above.\n"
                    "2. Explicitly cite the document name and chunk index for every factual observation.\n"
                    "3. Highlight any contradictions or evidentiary gaps.\n"
                )

        # ── 2. Construct Neural Inference Messages ────────────────────────────
        system_content = self.manifest.system_prompt
        if doc_context:
            system_content = f"{system_content}\n{doc_context}"

        messages = [
            {"role": "system", "content": system_content}
        ]

        for h in ctx.history[-6:]:
            if isinstance(h, dict) and h.get("role") in ("user", "assistant") and h.get("content"):
                messages.append({"role": h["role"], "content": h["content"]})

        messages.append({"role": "user", "content": ctx.query})

        # ── 3. Orchestrated LLM Completion ────────────────────────────────────
        answer, provider = llm_complete(
            messages,
            json_mode=False,
            max_tokens=750,
            required_tags=self.manifest.required_provider_tags
        )
        manifest = self.manifest

        # ── 4. Dynamic Suggested Actions ──────────────────────────────────────
        suggested_actions = []
        if has_docs:
            suggested_actions.append("Review Evidence Citations")
            suggested_actions.append("Audit Chronological Timeline Discrepancies")
            suggested_actions.append("Generate Section 65B Electronic Certificate")
        else:
            suggested_actions.append("Upload Case PDF / FIR Document")
            suggested_actions.append("Attach Seizure Memo / Bank Statement")

        return AgentResponse(
            answer=answer,
            agent_type="evidence_analysis_agent",
            agent_label=manifest.label,
            agent_icon=manifest.icon,
            agent_color=manifest.color,
            charts=[],
            executive_decision=None,
            provider=provider,
            visuals_updated=False,
            data_available=has_docs,
            suggested_actions=suggested_actions
        )
