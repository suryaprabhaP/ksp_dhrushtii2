"""
KSP Sentinel AI — Analytical Agent (SOLID: SRP + LSP)
"""
from app.config import KSP_ANALYTICAL_PROMPT
from app.core.interfaces import AgentManifest, AgentResponse, BaseAgent, ExecutionContext
from app.engine.session_store import session_store
from app.engine.visual_intelligence import parse_dual_stream_response
from app.providers.orchestrator import llm_complete
from app.services.quickml_service import quickml_service


class AnalyticalAgent(BaseAgent):
    """
    SRP: Handles multi-dimensional crime analytics, trends, rankings, and asset deficits,
         plus Zoho Catalyst QuickML Caseload Regression forecasting.
    Output: Dual-Stream Executive Command Briefing + Dynamic Visual Intelligence Suite.
    """
    @property
    def manifest(self) -> AgentManifest:
        return AgentManifest(
            intent_name="ANALYTICAL",
            label="Analytics Agent",
            icon="📊",
            color="#0ea5e9",
            description="Trigger when the query asks to generate visual charts (line, bar, doughnut), statistical trends, rankings, monthly trajectories, caseload forecasting, or financial comparisons.",
            requires_visual_studio=True,
            system_prompt=KSP_ANALYTICAL_PROMPT,
            trigger_examples=[
                "Show me theft trends and station ranking",
                "I need a time series chart for this",
                "Compare financial loss vs recovery",
                "Monthly trajectory of crime in 2025 and 2026",
                "Predict the caseload for ATM Gas Cutter Raids in September",
                "Forecast vehicle theft numbers for Q4"
            ]
        )

    def execute(self, ctx: ExecutionContext) -> AgentResponse:
        if ctx.deadline is not None:
            ctx.check_cancellation()

        # Check if query is an explicit QuickML predictive caseload forecast
        q_lower = ctx.query.lower()
        quickml_forecast_context = ""
        if any(w in q_lower for w in ["predict", "forecast", "caseload", "projection", "estimate cases", "future count"]):
            # Extract basic params with sensible defaults
            year = 2025 if "2025" in q_lower else (2026 if "2026" in q_lower else 2024)
            month = "September" if "sept" in q_lower else ("October" if "oct" in q_lower else ("December" if "dec" in q_lower else "General"))
            category = "Vehicle Theft" if "vehicle" in q_lower else ("Organized Robbery" if "robbery" in q_lower or "atm" in q_lower or "gas cutter" in q_lower else "Cyber Financial Fraud")
            subcat = "ATM Gas Cutter Raid" if "gas cutter" in q_lower or "atm" in q_lower else "General"
            
            caseload_res = quickml_service.predict_crime_caseload(
                crime_year=year,
                crime_month=month,
                crime_category=category,
                crime_subcategory=subcat
            )
            quickml_forecast_context = (
                f"\n[Zoho Catalyst QuickML Regression Forecast]\n"
                f"- Model: KSP_CrimeStatistics_5000 ({caseload_res.source})\n"
                f"- Predicted Incident Volume: {caseload_res.predicted_case_count} cases\n"
                f"- Model Confidence: {caseload_res.confidence * 100 if caseload_res.confidence <= 1.0 else caseload_res.confidence}%\n"
                f"- Evaluated Horizon: {month} {year} | Category: {category} ({subcat})\n"
            )

        # Chain of Responsibility: Check if dataset exists in session
        if not ctx.session_id or not session_store.has_dataset(ctx.session_id):
            explicit_chart = any(w in q_lower for w in ["chart", "plot", "line graph", "bar chart", "pie chart", "doughnut", "histogram", "scatter", "visualize", "draw a graph", "trend", "accused count", "ranking", "cases by", "districts by", "distribution"])
            if explicit_chart and not quickml_forecast_context:
                return AgentResponse(
                    answer="⚠️ **No Investigation Dataset Uploaded Yet**\n\nTo generate Section 65B-compliant statistical charts, trends, and rankings, please upload your investigation dataset (CSV, Excel, or JSON). Once uploaded, I will analyze your records and render the visual dashboard immediately.",
                    agent_type="analytical_agent",
                    agent_label=self.manifest.label,
                    agent_icon=self.manifest.icon,
                    agent_color=self.manifest.color,
                    charts=[],
                    executive_decision=None,
                    provider="data_guard",
                    visuals_updated=False,
                    data_available=False,
                    suggested_actions=["📁 Upload Case Dataset"]
                )
            if not explicit_chart and not quickml_forecast_context:
                # Graceful handoff to DocumentAgent (Zoho QuickML Knowledge Base RAG)
                return AgentResponse(
                    answer="",
                    agent_type="analytical_agent",
                    agent_label=self.manifest.label,
                    agent_icon=self.manifest.icon,
                    agent_color=self.manifest.color,
                    charts=[],
                    executive_decision=None,
                    provider="chain_of_responsibility",
                    handoff_target="DOCUMENT"
                )

        target_table = session_store.get_table_for_query(ctx.session_id, ctx.query) if ctx.session_id else None
        schema_summary = session_store.get_schema_summary(ctx.session_id, table_name=target_table) if ctx.session_id else ""
        system_content = (
            f"Operational division: {ctx.division}. Active Table: '{target_table}'. "
            f"Table Schema in DuckDB: {schema_summary}. "
            f"{quickml_forecast_context}"
            f"You MUST generate a tailored 'visual_suite' matching the query and 'executive_briefing'."
        )
        messages = [
            {"role": "system", "content": self.manifest.system_prompt},
            {"role": "system", "content": system_content}
        ]
        for h in ctx.history[-8:]:
            if h.get("role") in ("user", "assistant") and h.get("content"):
                messages.append({"role": h["role"], "content": h["content"]})
        
        if ctx.deadline is not None:
            ctx.check_cancellation()

        timeout_budget = ctx.get_remaining_budget() if ctx.deadline is not None else None
        raw_output, provider = llm_complete(
            messages,
            json_mode=True,
            required_tags=self.manifest.required_provider_tags,
            timeout=timeout_budget
        )
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
