"""
KSP Sentinel AI — Analytical Agent (SOLID: SRP + LSP)
"""
from app.config import KSP_ANALYTICAL_PROMPT
from app.core.interfaces import AgentManifest, AgentResponse, BaseAgent, ExecutionContext
from app.engine.session_store import session_store
from app.engine.visual_intelligence import parse_dual_stream_response
from app.providers.orchestrator import llm_complete


class AnalyticalAgent(BaseAgent):
    """
    SRP: Handles multi-dimensional crime analytics, trends, rankings, and asset deficits.
    Output: Dual-Stream Executive Command Briefing + Dynamic Visual Intelligence Suite.
    """
    @property
    def manifest(self) -> AgentManifest:
        return AgentManifest(
            intent_name="ANALYTICAL",
            label="Analytics Agent",
            icon="📊",
            color="#0ea5e9",
            description="Trigger when the query asks to generate visual charts (line, bar, doughnut), statistical trends, rankings, monthly trajectories, or financial comparisons.",
            requires_visual_studio=True,
            system_prompt=KSP_ANALYTICAL_PROMPT,
            trigger_examples=[
                "Show me theft trends and station ranking",
                "I need a time series chart for this",
                "Compare financial loss vs recovery",
                "Monthly trajectory of crime in 2025 and 2026"
            ]
        )

    def execute(self, ctx: ExecutionContext) -> AgentResponse:
        target_table = session_store.get_table_for_query(ctx.session_id, ctx.query) if ctx.session_id else None
        schema_summary = session_store.get_schema_summary(ctx.session_id, table_name=target_table) if ctx.session_id else ""
        messages = [
            {"role": "system", "content": self.manifest.system_prompt},
            {"role": "system", "content": f"Operational division: {ctx.division}. Active Table: '{target_table}'. Table Schema in DuckDB: {schema_summary}. You MUST generate a tailored 'visual_suite' matching the query and 'executive_briefing'."}
        ]
        for h in ctx.history[-8:]:
            if h.get("role") in ("user", "assistant") and h.get("content"):
                messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": ctx.query})

        raw_output, provider = llm_complete(messages, json_mode=True)
        answer, charts, decision = parse_dual_stream_response(raw_output, session_id=ctx.session_id, user_query=ctx.query)

        manifest = self.manifest
        return AgentResponse(
            answer=answer,
            agent_type="analytical_agent",
            agent_label=manifest.label,
            agent_icon=manifest.icon,
            agent_color=manifest.color,
            charts=charts,
            executive_decision=decision,
            provider=provider,
            visuals_updated=True
        )
