"""
KSP Sentinel AI — Federated Agent (SOLID: Orchestrator)
"""
import concurrent.futures
import logging
import time
from app.config import KSP_FEDERATED_PROMPT, FEDERATED_MAX_WORKERS
from app.core.interfaces import BaseAgent, ExecutionContext, AgentResponse, AgentManifest
from app.agents.analytical import AnalyticalAgent
from app.agents.graph import GraphAgent
from app.providers.orchestrator import orchestrator

log = logging.getLogger("standalone.agents.federated")

# Configurable Module-Level Thread Pool (Bounded Concurrency Control)
executor = concurrent.futures.ThreadPoolExecutor(
    max_workers=FEDERATED_MAX_WORKERS,
    thread_name_prefix="FedWorker"
)


class FederatedAgent(BaseAgent):
    GLOBAL_BUDGET: float = 6.5  # Application latency budget target (1.5s safety margin under 8.0s gateway)
    FANOUT_BUDGET: float = 4.0  # Strict sub-budget for parallel fan-out phase

    @property
    def manifest(self) -> AgentManifest:
        return AgentManifest(
            intent_name="FEDERATED",
            label="KSP Federated Intelligence",
            icon="🌐",
            color="#a855f7",
            description="Trigger when query asks for both analytical trends and network topology.",
            requires_visual_studio=True,
            system_prompt=KSP_FEDERATED_PROMPT,
            trigger_examples=["trajectory and trace the network"]
        )

    def execute(self, ctx: ExecutionContext) -> AgentResponse:
        log.info(f"[FederatedAgent] Executing parallel fan-out dispatch for query: {ctx.query}")
        
        # 1. Establish Immutable Request Deadline if not already initialized
        if ctx.deadline is None:
            ctx.set_deadline(self.GLOBAL_BUDGET)

        fanout_deadline = min(ctx.deadline, time.monotonic() + self.FANOUT_BUDGET)
        
        # 2. Instantiate Sub-Agents
        analytics_agent = AnalyticalAgent()
        graph_agent = GraphAgent()
        
        # 3. Parallel Fan-Out Execution
        log.info("[FederatedAgent] -> Spawning Analytics & Graph Sub-Tasks in parallel")
        future_analytics = executor.submit(analytics_agent.execute, ctx)
        future_graph = executor.submit(graph_agent.execute, ctx)
        
        fanout_remaining = max(0.0, fanout_deadline - time.monotonic())
        done, pending = concurrent.futures.wait(
            [future_analytics, future_graph],
            timeout=fanout_remaining,
            return_when=concurrent.futures.ALL_COMPLETED
        )
        
        # 4. Bounded Fan-In & Controlled Partial Degradation
        analytics_res = None
        if future_analytics in done:
            try:
                analytics_res = future_analytics.result()
            except Exception as e:
                log.warning(f"[FederatedAgent] Analytics Sub-Task exception: {e}")
        else:
            log.warning("[FederatedAgent] Analytics Sub-Task exceeded fan-out budget (degraded)")

        graph_res = None
        if future_graph in done:
            try:
                graph_res = future_graph.result()
            except Exception as e:
                log.warning(f"[FederatedAgent] Graph Sub-Task exception: {e}")
        else:
            log.warning("[FederatedAgent] Graph Sub-Task exceeded fan-out budget (degraded)")
            
        analytics_answer = analytics_res.answer if analytics_res else "⚠️ [Analytics Sub-Task Unavailable / Timed Out]"
        graph_answer = graph_res.answer if graph_res else "⚠️ [Network Forensic Sub-Task Unavailable / Timed Out]"

        # 5. Merge Visual Intelligence & Decisions
        combined_charts = []
        if analytics_res and analytics_res.charts:
            combined_charts.extend(analytics_res.charts)
        if graph_res and graph_res.charts:
            combined_charts.extend(graph_res.charts)
            
        # 6. Bounded Synthesis using Remaining Global Budget
        remaining_synthesis_budget = ctx.get_remaining_budget()
        log.info(f"[FederatedAgent] Remaining synthesis budget: {remaining_synthesis_budget:.2f}s")

        synthesis_input = f"""OFFICER QUERY: "{ctx.query}"

SUB-AGENT REPORTS:

1. ANALYTICS INVESTIGATIVE REPORT:
{analytics_answer}

2. NETWORK FORENSIC REPORT:
{graph_answer}
"""
        if remaining_synthesis_budget > 0.2:
            try:
                synthesized_answer = orchestrator.generate_completion(
                    prompt=synthesis_input,
                    system_instruction=self.manifest.system_prompt,
                    max_tokens=2000,
                    required_tags=self.manifest.required_provider_tags,
                    timeout=remaining_synthesis_budget
                )
            except Exception as e:
                log.warning(f"[FederatedAgent] Synthesis exception or timeout: {e}")
                synthesized_answer = f"### 🌐 Federated Intelligence Briefing (Degraded Mode)\n\n**Analytics:**\n{analytics_answer}\n\n**Network:**\n{graph_answer}"
        else:
            log.warning("[FederatedAgent] Global deadline expired before synthesis completion.")
            synthesized_answer = f"### 🌐 Federated Intelligence Briefing (Deadline Expired)\n\n**Analytics:**\n{analytics_answer}\n\n**Network:**\n{graph_answer}"
        
        return AgentResponse(
            answer=synthesized_answer,
            agent_type="federated_agent",
            agent_label="KSP Federated Intelligence",
            agent_icon="🌐",
            agent_color="#a855f7",
            charts=combined_charts,
            executive_decision=(analytics_res.executive_decision if analytics_res else None) or (graph_res.executive_decision if graph_res else None),
            provider="groq",
            visuals_updated=bool((analytics_res and analytics_res.visuals_updated) or (graph_res and graph_res.visuals_updated)),
            data_available=bool((analytics_res and analytics_res.data_available) or (graph_res and graph_res.data_available)),
            suggested_actions=["Review unified intelligence dossier", "Export federated report"]
        )
