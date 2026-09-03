"""
KSP Sentinel AI — Document & Legal Agent Facade (SOLID: SRP + LSP + DIP)
Handles legal statutory law (BNS/BNSS/BSA), SOP circulars, FIR filings,
and session-isolated document/PDF evidence synthesis with citations.
Composes LegalKnowledgeAgent (Global Base Agent) and EvidenceAnalysisAgent (Session Sandbox).
"""
import logging
from typing import List, Optional
from app.config import KSP_DOCUMENT_PROMPT
from app.core.interfaces import AgentManifest, AgentResponse, BaseAgent, ExecutionContext, IDocumentRepository
from app.engine.catalyst_document_store import catalyst_document_store
from app.agents.legal import LegalKnowledgeAgent
from app.agents.evidence import EvidenceAnalysisAgent

log = logging.getLogger("standalone.agents.document")


class DocumentAgent(BaseAgent):
    """
    SRP: Unified facade for Legal Statutory Reasoning and Session Evidence RAG.
    DIP: Injects IDocumentRepository (CatalystCloudDocumentStore).
    LSP: Returns standardized AgentResponse contract matching all frontend expectations.
    """
    def __init__(
        self,
        doc_repo: Optional[IDocumentRepository] = None,
        legal_agent: Optional[LegalKnowledgeAgent] = None,
        evidence_agent: Optional[EvidenceAnalysisAgent] = None
    ):
        self.doc_repo = doc_repo or catalyst_document_store
        self._legal_agent = legal_agent or LegalKnowledgeAgent()
        self._evidence_agent = evidence_agent or EvidenceAnalysisAgent(doc_repo=self.doc_repo)

    @property
    def manifest(self) -> AgentManifest:
        return AgentManifest(
            intent_name="DOCUMENT",
            label="Document & Legal Agent",
            icon="📄",
            color="#10b981",
            description="Trigger for legal sections (IPC, BNS, BNSS, BSA, IT Act, CrPC), FIR filing procedures, Section 65B certification, evidence PDFs, or statutory police SOPs.",
            requires_visual_studio=False,
            system_prompt=KSP_DOCUMENT_PROMPT,
            required_provider_tags=["rag_document", "free_reasoning"]
        )

    def execute(self, ctx: ExecutionContext) -> AgentResponse:
        session_id = ctx.session_id or "default_session"
        has_docs = self.doc_repo.has_documents(session_id)

        # Polymorphic Delegation: If session contains uploaded evidence, use EvidenceAnalysisAgent
        if has_docs:
            log.info(f"[DocumentAgent] Active session documents detected for '{session_id}'. Delegating to EvidenceAnalysisAgent.")
            resp = self._evidence_agent.execute(ctx)
            resp.agent_type = "document_agent"
            resp.agent_label = self.manifest.label
            resp.agent_icon = self.manifest.icon
            resp.agent_color = self.manifest.color
            return resp

        # Otherwise, delegate to the Global Legal Knowledge Base
        log.info(f"[DocumentAgent] No session documents for '{session_id}'. Delegating to LegalKnowledgeAgent (Global Cloud RAG).")
        resp = self._legal_agent.execute(ctx)
        resp.agent_type = "document_agent"
        resp.agent_label = self.manifest.label
        resp.agent_icon = self.manifest.icon
        resp.agent_color = self.manifest.color
        return resp

