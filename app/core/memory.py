"""
KSP Sentinel AI — Autonomous Session Memory & Cloud State Manager (SOLID: SRP + DIP)
===================================================================================
Maintains long-term session context by utilizing a Hybrid Cloud State Model:
1. Zoho Catalyst Cache (Redis-backed segment 54626000000136060 for sub-2ms reads/writes)
2. Zoho Catalyst Data Store (SessionMemory table for permanent cloud persistence)
3. Local SQLite/In-Memory fallback for 100% offline local development
"""
import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from app.config import (
    ENABLE_MEMORY_COMPRESSION,
    KSP_MEMORY_PROMPT,
    MEMORY_COMPRESS_THRESHOLD,
    MEMORY_WINDOW_SIZE,
)
from app.engine.session_store import session_store
from app.providers.orchestrator import llm_reasoning_complete
from app.services.catalyst_service import catalyst_cache_service, catalyst_datastore_service

log = logging.getLogger("standalone.memory")


class MemoryAgent:
    """
    SRP: Manages stateful conversation turns, cloud cache, and context compression.
    DIP: Decoupled via CatalystCacheService and CatalystDataStoreService with SQLite fallback.
    """

    @classmethod
    def init_memory_table(cls, session_id: str):
        """Ensures the local session_memory SQLite table exists for offline fallback."""
        try:
            con = session_store.get_connection(session_id)
            con.execute("""
                CREATE TABLE IF NOT EXISTS session_memory (
                    session_id TEXT PRIMARY KEY,
                    summary TEXT,
                    turn_count INTEGER,
                    updated_at TEXT,
                    history_json TEXT,
                    last_agent_type TEXT
                )
            """)
        except Exception as e:
            log.warning(f"[MemoryAgent] Local session_memory table notice: {e}")

    @classmethod
    def get_session_history(cls, session_id: str) -> Tuple[List[Dict[str, Any]], Optional[str], Optional[str]]:
        """
        Retrieves stateful message history, active memory summary, and last agent type.
        Execution Flow (Cache-Aside Pattern):
        1. Check Zoho Catalyst Redis Cache (Sub-2ms)
        2. Fallback to Zoho Catalyst Data Store (ZCQL)
        3. Fallback to Local SQLite
        """
        if not session_id:
            return [], None, None

        # ── 1. Check Catalyst Cache (Redis Segment 54626000000136060) ─────────
        try:
            cached = catalyst_cache_service.get_session(session_id)
            if cached and isinstance(cached, dict):
                history = cached.get("history", [])
                summary = cached.get("summary")
                last_agent = cached.get("last_agent_type")
                if history or summary:
                    log.debug(f"[MemoryAgent] Cache hit for session '{session_id}' ({len(history)} turns)")
                    return history, summary or None, last_agent or None
        except Exception as e:
            log.debug(f"[MemoryAgent] Cache check notice: {e}")

        # ── 2. Fallback to Catalyst Data Store Table 'SessionMemory' ───────────
        try:
            cloud_row = catalyst_datastore_service.get_session_memory(session_id)
            if cloud_row and isinstance(cloud_row, dict):
                raw_json = cloud_row.get("history_json")
                summary = cloud_row.get("summary")
                last_agent = cloud_row.get("last_agent_type")
                history = []
                if raw_json:
                    try:
                        history = json.loads(raw_json) if isinstance(raw_json, str) else raw_json
                    except Exception:
                        history = []

                # Populate Cache for subsequent sub-2ms reads
                catalyst_cache_service.put_session(session_id, {
                    "history": history,
                    "summary": summary,
                    "last_agent_type": last_agent,
                    "turn_count": len(history)
                })
                log.info(f"[MemoryAgent] Data Store hit for session '{session_id}' ({len(history)} turns)")
                return history, summary or None, last_agent or None
        except Exception as e:
            log.debug(f"[MemoryAgent] Cloud Data Store check notice: {e}")

        # ── 3. Fallback to Local SQLite ───────────────────────────────────────
        try:
            cls.init_memory_table(session_id)
            con = session_store.get_connection(session_id)
            row = con.execute(
                "SELECT history_json, summary, last_agent_type FROM session_memory WHERE session_id = ?",
                [session_id]
            ).fetchone()

            if not row:
                return [], None, None

            raw_history_json, summary, last_agent_type = row[0], row[1], row[2]
            history: List[Dict[str, Any]] = []
            if raw_history_json:
                try:
                    history = json.loads(raw_history_json)
                except Exception as je:
                    log.warning(f"[MemoryAgent] Deserialization notice for '{session_id}': {je}")

            return history, summary or None, last_agent_type or None
        except Exception as e:
            log.warning(f"[MemoryAgent] Local session retrieval notice for '{session_id}': {e}")
            return [], None, None

    @classmethod
    def save_session_turn(
        cls,
        session_id: str,
        role: str,
        content: str,
        agent_type: Optional[str] = None
    ):
        """
        Appends a conversation turn to the stateful history across Cache, Data Store, and SQLite.
        Automatically triggers semantic compression if turns exceed threshold.
        """
        if not session_id or not content:
            return
        try:
            cls.init_memory_table(session_id)
            history, summary, last_agent = cls.get_session_history(session_id)

            new_turn = {
                "role": role,
                "content": content,
                "agent_type": agent_type or last_agent or "CONVERSATIONAL",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            history.append(new_turn)

            effective_last_agent = agent_type if agent_type else last_agent

            # Compression trigger if history exceeds window threshold
            if ENABLE_MEMORY_COMPRESSION and len(history) > MEMORY_COMPRESS_THRESHOLD:
                try:
                    history, summary = cls._compress_old_turns(session_id, history, summary)
                except Exception as ce:
                    log.error(f"[MemoryAgent] Semantic compression notice: {ce}", exc_info=True)

            now_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            turn_count = len(history)

            # 1. Update High-Speed Catalyst Cache (Sub-2ms)
            catalyst_cache_service.put_session(session_id, {
                "history": history,
                "summary": summary,
                "last_agent_type": effective_last_agent,
                "turn_count": turn_count
            })

            # 2. Asynchronous Background Write to Catalyst Data Store Table
            catalyst_datastore_service.upsert_session_memory(
                session_id=session_id,
                summary=summary,
                history=history,
                last_agent_type=effective_last_agent,
                turn_count=turn_count
            )

            # 3. Update Local SQLite for offline dev consistency
            con = session_store.get_connection(session_id)
            con.execute("""
                INSERT OR REPLACE INTO session_memory (session_id, summary, turn_count, updated_at, history_json, last_agent_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [session_id, summary, turn_count, now_str, json.dumps(history), effective_last_agent])

            log.info(f"[MemoryAgent] Saved turn for '{session_id}' [{role}|agent:{effective_last_agent}] Total turns: {turn_count}")
        except Exception as e:
            log.warning(f"[MemoryAgent] Error saving session turn: {e}", exc_info=True)

    @classmethod
    def _compress_old_turns(
        cls,
        session_id: str,
        history: List[Dict[str, Any]],
        existing_summary: Optional[str]
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Compresses turns older than recent 4 turns into an updated rolling summary.
        Preserves critical investigation entities.
        """
        if len(history) <= 4:
            return history, existing_summary

        turns_to_compress = history[:-4]
        recent_turns = history[-4:]

        history_str = ""
        if existing_summary:
            history_str += f"Prior Investigation Baseline: {existing_summary}\n\n"

        for msg in turns_to_compress:
            role_label = "Officer" if msg.get("role") == "user" else "KSP Sentinel AI"
            cnt = str(msg.get("content") or "").strip()
            if cnt:
                history_str += f"{role_label}: {cnt}\n"

        if not history_str.strip():
            return history, existing_summary

        log.info(f"[MemoryAgent] Compressing {len(turns_to_compress)} turns for session '{session_id}'...")

        messages = [
            {"role": "system", "content": KSP_MEMORY_PROMPT},
            {
                "role": "user",
                "content": (
                    "Compress the following police investigation conversation into a 2-3 sentence rolling summary. "
                    "Explicitly preserve suspect names, locations, crime categories, FIR numbers, and key directives:\n\n"
                    f"{history_str}"
                )
            }
        ]

        summary, _ = llm_reasoning_complete(messages, json_mode=False, max_tokens=250)
        summary = summary.strip()
        if "</think>" in summary:
            summary = summary.split("</think>")[-1].strip()

        log.info(f"[MemoryAgent] New rolling memory summary generated: '{summary[:80]}...'")
        return recent_turns, summary

    @classmethod
    def compress_history(
        cls,
        session_id: str,
        history: List[Dict[str, Any]],
        existing_summary: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Public entrypoint for compressing conversation history turns.
        """
        return cls._compress_old_turns(session_id, history, existing_summary)

    @classmethod
    def get_memory_summary(cls, session_id: str) -> Optional[str]:
        """Backward-compatible summary getter."""
        _, summary, _ = cls.get_session_history(session_id)
        return summary

    @classmethod
    def save_memory_summary(cls, session_id: str, summary: str, turn_count: int):
        """Backward-compatible summary setter."""
        if not session_id or not summary:
            return
        try:
            cls.init_memory_table(session_id)
            con = session_store.get_connection(session_id)
            now_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            con.execute("""
                INSERT OR REPLACE INTO session_memory (session_id, summary, turn_count, updated_at, history_json, last_agent_type)
                VALUES (?, ?, ?, ?, COALESCE((SELECT history_json FROM session_memory WHERE session_id = ?), '[]'), COALESCE((SELECT last_agent_type FROM session_memory WHERE session_id = ?), 'CONVERSATIONAL'))
            """, [session_id, summary, turn_count, now_str, session_id, session_id])
        except Exception as e:
            log.warning(f"[MemoryAgent] Error saving memory summary: {e}")
