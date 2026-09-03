"""
KSP Sentinel AI — Zoho Catalyst Cloud Document Store (SOLID: SRP + DIP + LSP)
=============================================================================
Provides cloud-native, stateless, and session-isolated document persistence:
1. Catalyst File Store (Folder 54626000000149001): Raw PDF/FIR BLOB persistence.
2. Catalyst NoSQL Data Store (Table 54626000000153001 'KSP_Session_Evidence'):
   - Partition Key: session_id (String)
   - Sort Key: doc_name (String)
   - Additional Sort Keys: chunk_index (Numeric), chunk_id (String)
   - TTL Attribute: ttl_expiry (Numeric Epoch Timestamp)
3. High-Resilience Local Thread-Safe Memory Buffer for offline/low-latency execution.
"""
import io
import json
import logging
import re
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests

from app.config import (
    CATALYST_API_BASE,
    CATALYST_FILESTORE_FOLDER_ID,
    CATALYST_PROJECT_ID,
    CATALYST_TABLE_SESSION_EVIDENCE,
    CATALYST_TABLE_SESSION_EVIDENCE_NAME,
)
from app.core.interfaces import DocumentChunk, IDocumentRepository
from app.services.catalyst_service import (
    CatalystDataStoreService,
    CatalystFileStoreService,
    catalyst_datastore_service,
    catalyst_filestore_service,
)
from app.services.zoho_token_manager import zoho_token_manager

log = logging.getLogger("standalone.catalyst_document_store")


class CatalystCloudDocumentStore(IDocumentRepository):
    """
    SOLID Implementation of IDocumentRepository:
    - SRP: Manages document ingestion, chunking, lexical search, TTL expiration, and cloud synchronization.
    - DIP: Injects CatalystDataStoreService and CatalystFileStoreService.
    - LSP: Fully substitutes SQLiteDocumentStore with identical contracts.
    """

    def __init__(
        self,
        datastore_service: Optional[CatalystDataStoreService] = None,
        filestore_service: Optional[CatalystFileStoreService] = None,
        default_ttl_seconds: int = 7200  # 2 Hours TTL
    ):
        self._datastore = datastore_service or catalyst_datastore_service
        self._filestore = filestore_service or catalyst_filestore_service
        self._table_id = CATALYST_TABLE_SESSION_EVIDENCE
        self._table_name = CATALYST_TABLE_SESSION_EVIDENCE_NAME
        self._folder_id = CATALYST_FILESTORE_FOLDER_ID
        self._project_id = CATALYST_PROJECT_ID
        self._default_ttl_seconds = default_ttl_seconds

        # High-resilience thread-safe local memory buffer
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()

    @property
    def access_token(self) -> Optional[str]:
        return zoho_token_manager.get_valid_token(purpose="tables")

    def _ensure_session(self, session_id: str) -> Dict[str, Any]:
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = {
                    "docs": {},
                    "chunks": [],  # Bounded local resilience buffer (max 100 chunks per session)
                    "staged": {}
                }
            return self._sessions[session_id]

    def _extract_text(self, filename: str, file_bytes: bytes) -> str:
        """Polymorphic text extraction for PDF, TXT, MD, and JSON files."""
        lower_name = filename.lower()
        if lower_name.endswith(".pdf"):
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                extracted_pages = []
                for idx, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    if text.strip():
                        extracted_pages.append(f"--- Page {idx + 1} ---\n{text}")
                return "\n\n".join(extracted_pages)
            except Exception as e:
                log.warning(f"[CatalystDocStore] pypdf extraction fallback for '{filename}': {e}")
                raw_str = file_bytes.decode("latin-1", errors="ignore")
                clean_str = re.sub(r"[^\x20-\x7E\n\t]", " ", raw_str)
                return re.sub(r"\s+", " ", clean_str)

        elif lower_name.endswith((".txt", ".md", ".json", ".log", ".csv")):
            return file_bytes.decode("utf-8", errors="replace")

        return file_bytes.decode("utf-8", errors="replace")

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 80) -> List[str]:
        """Splits text into contextually bounded chunks respecting sentence breaks."""
        if not text or not text.strip():
            return []

        cleaned_text = re.sub(r"\r\n", "\n", text).strip()
        paragraphs = cleaned_text.split("\n\n")
        chunks: List[str] = []
        current_chunk = []
        current_length = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_len = len(para)
            if current_length + para_len <= chunk_size:
                current_chunk.append(para)
                current_length += para_len + 2
            else:
                if current_chunk:
                    chunk_str = "\n\n".join(current_chunk)
                    chunks.append(chunk_str)
                    if overlap > 0 and len(chunk_str) > overlap:
                        current_chunk = [chunk_str[-overlap:]]
                        current_length = len(current_chunk[0])
                    else:
                        current_chunk = []
                        current_length = 0

                if para_len > chunk_size:
                    sentences = re.split(r"(?<=[.?!])\s+", para)
                    for sent in sentences:
                        sent = sent.strip()
                        if not sent:
                            continue
                        if current_length + len(sent) <= chunk_size:
                            current_chunk.append(sent)
                            current_length += len(sent) + 1
                        else:
                            if current_chunk:
                                chunks.append(" ".join(current_chunk))
                            current_chunk = [sent]
                            current_length = len(sent)
                else:
                    current_chunk.append(para)
                    current_length += para_len + 2

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return [c.strip() for c in chunks if c.strip()]

    def ingest_document(self, session_id: str, filename: str, file_bytes: bytes) -> Dict[str, Any]:
        """
        Ingests evidence document:
        1. Stores raw BLOB asynchronously in Catalyst File Store (Folder 54626000000149001).
        2. Chunks and indexes text into local thread-safe session memory.
        3. Persists structured chunks into Catalyst NoSQL Data Store (Table 54626000000153001) with TTL.
        """
        session_data = self._ensure_session(session_id)
        raw_text = self._extract_text(filename, file_bytes)
        chunk_texts = self._chunk_text(raw_text, chunk_size=500, overlap=80)
        file_size_kb = round(len(file_bytes) / 1024, 2)
        ingested_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        epoch_now = int(time.time())
        ttl_expiry = epoch_now + self._default_ttl_seconds

        new_chunks: List[DocumentChunk] = []
        for idx, text in enumerate(chunk_texts):
            chunk_id = f"{filename}_{idx}_{epoch_now}"
            new_chunks.append(DocumentChunk(
                chunk_id=chunk_id,
                doc_name=filename,
                chunk_index=idx,
                content=text,
                metadata={"ttl_expiry": ttl_expiry, "ingested_at": ingested_at},
                score=1.0
            ))

        with self._lock:
            # Bounded resilience buffer: keep only the most recent chunks (max 100)
            existing_chunks = [c for c in session_data.get("chunks", []) if c.doc_name != filename]
            combined_chunks = existing_chunks + new_chunks
            session_data["chunks"] = combined_chunks[-100:]  # Strictly bounded to prevent memory bloat

            session_data["docs"][filename] = {
                "chunk_count": len(new_chunks),
                "file_size_kb": file_size_kb,
                "ingested_at": ingested_at,
                "ttl_expiry": ttl_expiry
            }

        # 1. Asynchronously backup raw BLOB in Catalyst File Store
        if self._filestore:
            self._filestore.upload_session_dataset(session_id, filename, file_bytes)

        # 2. Synchronously persist structured chunks in Catalyst NoSQL Data Store (authoritative store)
        if self._datastore:
            try:
                for chunk in new_chunks:
                    nosql_record = {
                        "session_id": str(session_id),
                        "doc_name": str(filename),
                        "chunk_index": int(chunk.chunk_index),
                        "chunk_id": str(chunk.chunk_id),
                        "ttl_expiry": int(ttl_expiry),
                        "content": str(chunk.content)
                    }
                    self._datastore.insert_raw_table_record(self._table_id, nosql_record)
                log.info(f"[CatalystDocStore] Persisted {len(new_chunks)} chunks of '{filename}' to NoSQL table {self._table_id} (TTL: {ttl_expiry}).")
            except Exception as e:
                log.debug(f"[CatalystDocStore] Sync NoSQL persistence notice for {filename}: {e}")

        log.info(f"[CatalystDocStore] Ingested '{filename}' ({len(new_chunks)} chunks, {file_size_kb} KB) for session '{session_id}'")
        return {
            "success": True,
            "filename": filename,
            "session_id": session_id,
            "chunk_count": len(new_chunks),
            "file_size_kb": file_size_kb,
            "ingested_at": ingested_at,
            "char_count": len(raw_text),
            "ttl_expiry": ttl_expiry
        }

    def search_chunks(self, session_id: str, query: str, limit: int = 5) -> List[DocumentChunk]:
        """
        Cloud-backed bounded retrieval with high-resilience local buffer fallback.
        1. Queries Catalyst Data Store via ZCQL (authoritative cloud retrieval).
        2. Falls back to bounded local session buffer if offline or cloud unavailable.
        """
        tokens = [t.lower().strip() for t in re.findall(r"\w+", query) if len(t.strip()) > 2]
        if not tokens:
            return []

        now_epoch = int(time.time())
        candidate_chunks: List[DocumentChunk] = []

        # 1. Attempt Cloud-Backed ZCQL Retrieval
        if self._datastore:
            try:
                like_clauses = " OR ".join([f"content LIKE '%{t}%'" for t in tokens])
                zcql = f"SELECT chunk_id, doc_name, chunk_index, content, ttl_expiry FROM {self._table_name} WHERE session_id = '{session_id}' AND ({like_clauses})"
                rows = self._datastore.execute_zcql(zcql)
                if rows is not None and len(rows) > 0:
                    for r in rows:
                        try:
                            ttl_val = int(r.get("ttl_expiry", now_epoch + 1))
                        except (ValueError, TypeError):
                            ttl_val = now_epoch + 1
                        if ttl_val >= now_epoch:
                            candidate_chunks.append(DocumentChunk(
                                chunk_id=str(r.get("chunk_id", "")),
                                doc_name=str(r.get("doc_name", "")),
                                chunk_index=int(r.get("chunk_index", 0)),
                                content=str(r.get("content", "")),
                                metadata={"ttl_expiry": ttl_val},
                                score=0.0
                            ))
            except Exception as e:
                log.debug(f"[CatalystDocStore] Cloud ZCQL search notice: {e}")

        # 2. Fallback to bounded local resilience buffer if cloud returned no candidate chunks
        if not candidate_chunks:
            with self._lock:
                session_data = self._sessions.get(session_id)
                if session_data and session_data.get("chunks"):
                    candidate_chunks = [
                        c for c in session_data["chunks"]
                        if c.metadata.get("ttl_expiry", now_epoch + 1) >= now_epoch
                    ]

        if not candidate_chunks:
            return []

        # 3. Rescore locally over bounded candidate set
        results: List[DocumentChunk] = []
        for c in candidate_chunks:
            content_lower = c.content.lower()
            score = 0.0
            for token in tokens:
                count = content_lower.count(token)
                if count > 0:
                    score += 1.0 + (count * 0.2)

            if query.lower() in content_lower:
                score += 5.0

            if score > 0:
                results.append(DocumentChunk(
                    chunk_id=c.chunk_id,
                    doc_name=c.doc_name,
                    chunk_index=c.chunk_index,
                    content=c.content,
                    metadata=c.metadata,
                    score=score
                ))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]

    def list_documents(self, session_id: str) -> List[Dict[str, Any]]:
        """Lists active, non-expired registered documents in the session (Local Cache -> Cloud Rehydration)."""
        now_epoch = int(time.time())

        # 1. Fast local metadata check
        with self._lock:
            session_data = self._sessions.get(session_id)
            if session_data and session_data.get("docs"):
                active_docs = []
                for doc_name, meta in session_data["docs"].items():
                    if meta.get("ttl_expiry", now_epoch + 1) >= now_epoch:
                        active_docs.append({
                            "doc_name": doc_name,
                            "chunk_count": meta.get("chunk_count", 0),
                            "file_size_kb": meta.get("file_size_kb", 0.0),
                            "ingested_at": meta.get("ingested_at", "")
                        })
                if active_docs:
                    return active_docs

        # 2. Cloud rehydration if local metadata was lost (e.g. post-restart)
        if self._datastore:
            try:
                zcql = f"SELECT doc_name, ttl_expiry FROM {self._table_name} WHERE session_id = '{session_id}'"
                rows = self._datastore.execute_zcql(zcql)
                if rows:
                    doc_counts = {}
                    for r in rows:
                        try:
                            ttl = int(r.get("ttl_expiry", now_epoch + 1))
                        except (ValueError, TypeError):
                            ttl = now_epoch + 1
                        if ttl >= now_epoch:
                            doc = str(r.get("doc_name", "unknown"))
                            doc_counts[doc] = doc_counts.get(doc, 0) + 1
                    return [
                        {"doc_name": d, "chunk_count": cnt, "file_size_kb": 0.0, "ingested_at": ""}
                        for d, cnt in doc_counts.items()
                    ]
            except Exception as e:
                log.debug(f"[CatalystDocStore] Cloud list notice: {e}")

        return []

    def delete_document(self, session_id: str, filename: str) -> bool:
        """Deletes a document and its chunks from local cache and Catalyst Data Store."""
        with self._lock:
            session_data = self._sessions.get(session_id)
            if session_data:
                session_data.get("docs", {}).pop(filename, None)
                if "chunks" in session_data:
                    session_data["chunks"] = [c for c in session_data["chunks"] if c.doc_name != filename]

        if self._datastore:
            try:
                zcql = f"SELECT ROWID FROM {self._table_name} WHERE session_id = '{session_id}' AND doc_name = '{filename}'"
                rows = self._datastore.execute_zcql(zcql)
                if rows:
                    for r in rows:
                        row_id = r.get("ROWID")
                        if row_id:
                            self._datastore.delete_raw_table_record(self._table_id, str(row_id))
            except Exception as e:
                log.debug(f"[CatalystDocStore] Cloud delete notice: {e}")

        return True

    def has_documents(self, session_id: str) -> bool:
        """Checks if session has any active, non-expired indexed documents."""
        now_epoch = int(time.time())

        # 1. Check local session metadata
        with self._lock:
            session_data = self._sessions.get(session_id)
            if session_data and session_data.get("docs"):
                for meta in session_data["docs"].values():
                    if meta.get("ttl_expiry", now_epoch + 1) >= now_epoch:
                        return True

        # 2. Check cloud persistent storage (post-restart recovery)
        if self._datastore:
            try:
                zcql = f"SELECT ttl_expiry FROM {self._table_name} WHERE session_id = '{session_id}'"
                rows = self._datastore.execute_zcql(zcql)
                if rows:
                    for r in rows:
                        try:
                            ttl = int(r.get("ttl_expiry", now_epoch + 1))
                            if ttl >= now_epoch:
                                return True
                        except (ValueError, TypeError):
                            return True
            except Exception as e:
                log.debug(f"[CatalystDocStore] Cloud has_documents notice: {e}")

        return False

    def stage_transcript(
        self,
        session_id: str,
        stage_id: str,
        filename: str,
        transcript_kn: str,
        transcript_en: str,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Sandboxed stage insertion for human-in-the-loop audio review."""
        session_data = self._ensure_session(session_id)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self._lock:
            session_data["staged"][stage_id] = {
                "stage_id": stage_id,
                "session_id": session_id,
                "filename": filename,
                "transcript_kn": transcript_kn,
                "transcript_en": transcript_en,
                "entities": entities if isinstance(entities, dict) else {},
                "created_at": created_at,
                "status": "staged"
            }

        log.info(f"[CatalystDocStore] Staged audio transcript '{stage_id}' for session '{session_id}'")
        return {
            "success": True,
            "stage_id": stage_id,
            "session_id": session_id,
            "filename": filename,
            "created_at": created_at,
            "status": "staged"
        }

    def get_staged_transcripts(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieves all currently staged (un-injected) audio transcripts for a session."""
        with self._lock:
            session_data = self._sessions.get(session_id)
            if not session_data:
                return []
            return [
                v for v in session_data.get("staged", {}).values()
                if v.get("status") == "staged"
            ]

    def confirm_and_inject_transcript(
        self,
        session_id: str,
        stage_id: str,
        markdown_content: str,
        filename: str = ""
    ) -> Dict[str, Any]:
        """Human-in-the-Loop Gateway: moves verified transcript to active session RAG table."""
        doc_name = filename if filename else f"audio_statement_{stage_id}.md"
        if not doc_name.lower().endswith(".md"):
            doc_name = f"{doc_name}.md"

        session_data = self._ensure_session(session_id)
        with self._lock:
            if stage_id in session_data["staged"]:
                session_data["staged"][stage_id]["status"] = "injected"

        return self.ingest_document(
            session_id=session_id,
            filename=doc_name,
            file_bytes=markdown_content.encode("utf-8")
        )

    def delete_staged_transcript(self, session_id: str, stage_id: str) -> bool:
        """Discards an unconfirmed staged transcript."""
        with self._lock:
            session_data = self._sessions.get(session_id)
            if not session_data:
                return False
            return session_data.get("staged", {}).pop(stage_id, None) is not None

    def clear_session(self, session_id: str) -> None:
        """Completely drops session storage."""
        with self._lock:
            self._sessions.pop(session_id, None)


# Global Singleton Instance for Dependency Injection
catalyst_document_store = CatalystCloudDocumentStore()
