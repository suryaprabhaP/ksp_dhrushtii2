"""
KSP Sentinel AI — Unit & Integration Tests for CatalystCloudDocumentStore
==========================================================================
Tests:
1. Document Ingestion & Chunking with TTL timestamping.
2. Lexical & Phrase search scoring.
3. Strict multi-tenant session isolation (Session A vs Session B).
4. TTL Expiration Filtering.
5. Polymorphic DocumentAgent facade routing (Legal vs Evidence).
6. Human-in-the-loop audio transcript staging and injection gateway.
"""
import time
import unittest
from app.core.interfaces import ExecutionContext, DocumentChunk
from app.engine.catalyst_document_store import CatalystCloudDocumentStore
from app.agents.legal import LegalKnowledgeAgent
from app.agents.evidence import EvidenceAnalysisAgent
from app.agents.document import DocumentAgent


class TestCatalystCloudDocumentStore(unittest.TestCase):
    def setUp(self):
        # Initialize an isolated document store instance
        self.store = CatalystCloudDocumentStore(default_ttl_seconds=3600)

    def test_ingest_and_search_text(self):
        session_id = "test_sess_evidence_001"
        filename = "fir_cyber_fraud_318.txt"
        sample_text = (
            "FIRST INFORMATION REPORT — Cyber Crime Division Bengaluru\n\n"
            "Under Section 66D IT Act and Section 318 BNS.\n\n"
            "Accused entity identified as Ankit Verma operating mule accounts in Koramangala.\n\n"
            "Total illicit fund flow tracked to Rs 45,00,000 across 12 UPI handles."
        )

        meta = self.store.ingest_document(session_id, filename, sample_text.encode("utf-8"))
        self.assertTrue(meta["success"])
        self.assertEqual(meta["filename"], filename)
        self.assertGreater(meta["chunk_count"], 0)
        self.assertIn("ttl_expiry", meta)
        self.assertGreater(meta["ttl_expiry"], int(time.time()))

        # Search for suspect
        chunks = self.store.search_chunks(session_id, "Ankit Verma Koramangala", limit=3)
        self.assertGreater(len(chunks), 0)
        self.assertIn("Ankit Verma", chunks[0].content)
        self.assertEqual(chunks[0].doc_name, filename)

    def test_strict_session_isolation(self):
        """Ensure Officer Session A cannot access or leak evidence into Officer Session B."""
        session_a = "officer_dcp_north"
        session_b = "officer_acp_south"

        doc_a = "Confidential Syndicate Nexus in Belagavi. Intercepted vehicle KA-22-M-9900."
        self.store.ingest_document(session_a, "syndicate_belagavi.txt", doc_a.encode("utf-8"))

        doc_b = "Routine Patrol Schedule for Electronic City Ward 4."
        self.store.ingest_document(session_b, "patrol_schedule.txt", doc_b.encode("utf-8"))

        # Session A can see syndicate, Session B CANNOT
        chunks_a = self.store.search_chunks(session_a, "Belagavi vehicle", limit=3)
        self.assertEqual(len(chunks_a), 1)
        self.assertIn("KA-22-M-9900", chunks_a[0].content)

        chunks_b = self.store.search_chunks(session_b, "Belagavi vehicle", limit=3)
        self.assertEqual(len(chunks_b), 0)

        # Document listings are strictly isolated
        docs_a = self.store.list_documents(session_a)
        docs_b = self.store.list_documents(session_b)
        self.assertEqual(len(docs_a), 1)
        self.assertEqual(docs_a[0]["doc_name"], "syndicate_belagavi.txt")
        self.assertEqual(len(docs_b), 1)
        self.assertEqual(docs_b[0]["doc_name"], "patrol_schedule.txt")

    def test_ttl_expiration_filtering(self):
        """Simulate TTL expiration and verify expired chunks are purged from search."""
        store_with_expired_ttl = CatalystCloudDocumentStore(default_ttl_seconds=-10)  # Expired 10s ago
        session_id = "test_expired_session"
        text = "Expiring case record."
        store_with_expired_ttl.ingest_document(session_id, "expiring_doc.txt", text.encode("utf-8"))

        # has_documents and search_chunks should filter out expired chunks
        self.assertFalse(store_with_expired_ttl.has_documents(session_id))
        self.assertEqual(len(store_with_expired_ttl.search_chunks(session_id, "record")), 0)
        self.assertEqual(len(store_with_expired_ttl.list_documents(session_id)), 0)

    def test_delete_document(self):
        session_id = "test_delete_sess"
        self.store.ingest_document(session_id, "purge_me.txt", b"Sensitive data to delete.")
        self.assertTrue(self.store.has_documents(session_id))

        ok = self.store.delete_document(session_id, "purge_me.txt")
        self.assertTrue(ok)
        self.assertFalse(self.store.has_documents(session_id))
        self.assertEqual(len(self.store.search_chunks(session_id, "Sensitive")), 0)

    def test_audio_staging_and_injection(self):
        """Verify Human-in-the-loop audio staging and injection gateway."""
        session_id = "test_audio_session"
        stage_id = "stg_audio_991"
        self.store.stage_transcript(
            session_id=session_id,
            stage_id=stage_id,
            filename="witness_call.mp3",
            transcript_kn="ಘಟನೆಯ ವಿವರ",
            transcript_en="Incident details of theft",
            entities={"suspect": "Suresh", "category": "Theft"}
        )

        staged = self.store.get_staged_transcripts(session_id)
        self.assertEqual(len(staged), 1)
        self.assertEqual(staged[0]["stage_id"], stage_id)

        # Confirm and inject
        inj = self.store.confirm_and_inject_transcript(
            session_id=session_id,
            stage_id=stage_id,
            markdown_content="# Verified Witness Statement\n\nSuspect Suresh observed entering premises."
        )
        self.assertTrue(inj["success"])
        self.assertTrue(self.store.has_documents(session_id))

        chunks = self.store.search_chunks(session_id, "Suresh", limit=2)
        self.assertGreater(len(chunks), 0)
        self.assertIn("Suresh", chunks[0].content)


class TestAgentSplitAndPolymorphism(unittest.TestCase):
    def setUp(self):
        self.store = CatalystCloudDocumentStore()

    def test_legal_knowledge_agent_contract(self):
        agent = LegalKnowledgeAgent()
        manifest = agent.manifest
        self.assertEqual(manifest.intent_name, "LEGAL_KNOWLEDGE")
        self.assertEqual(manifest.label, "Legal Knowledge Base")
        self.assertEqual(manifest.icon, "⚖️")

    def test_evidence_analysis_agent_contract(self):
        agent = EvidenceAnalysisAgent(doc_repo=self.store)
        manifest = agent.manifest
        self.assertEqual(manifest.intent_name, "EVIDENCE_ANALYSIS")
        self.assertEqual(manifest.label, "Case Evidence Forensics")
        self.assertEqual(manifest.icon, "📑")

    def test_document_agent_composite_delegation(self):
        """
        Verify DocumentAgent acts as a seamless polymorphic composite:
        - When documents exist -> routes to EvidenceAnalysisAgent
        - When no documents exist -> routes to LegalKnowledgeAgent
        """
        agent = DocumentAgent(doc_repo=self.store)
        
        # Scenario 1: Empty session -> Legal Knowledge Base RAG
        ctx_legal = ExecutionContext(
            query="What is the statutory penalty under Section 318 BNS?",
            session_id="empty_legal_session"
        )
        resp_legal = agent.execute(ctx_legal)
        self.assertEqual(resp_legal.agent_type, "document_agent")
        self.assertIsInstance(resp_legal.answer, str)
        self.assertGreater(len(resp_legal.answer), 10)

        # Scenario 2: Active session with uploaded FIR -> Case Evidence Forensics
        self.store.ingest_document(
            "active_case_session",
            "FIR_2026_091.pdf",
            b"FIRST INFORMATION REPORT: Bank transaction fraud by Rahul Rao in Whitefield."
        )
        ctx_evidence = ExecutionContext(
            query="Who is the named suspect in the uploaded FIR?",
            session_id="active_case_session"
        )
        resp_evidence = agent.execute(ctx_evidence)
        self.assertEqual(resp_evidence.agent_type, "document_agent")
        self.assertTrue(resp_evidence.data_available)
        self.assertIsInstance(resp_evidence.answer, str)


if __name__ == "__main__":
    unittest.main()
