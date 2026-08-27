"""
KSP Sentinel AI — Federated Agent (SOLID: Orchestrator)
"""
import logging
from app.core.interfaces import BaseAgent, ExecutionContext, AgentResponse, AgentManifest
from app.agents.analytical import AnalyticalAgent
from app.agents.graph import GraphAgent
from app.providers.orchestrator import orchestrator

log = logging.getLogger("standalone.agents.federated")

class FederatedAgent(BaseAgent):
    @property
    def manifest(self) -> AgentManifest:
        return AgentManifest(
            intent_name="FEDERATED",
            label="KSP Federated Intelligence",
            icon="🌐",
            color="#a855f7",
            description="Trigger when query asks for both analytical trends and network topology.",
            requires_visual_studio=True,
            system_prompt="You are a federated synthesizer.",
            trigger_examples=["trajectory and trace the network"]
        )

    def execute(self, ctx: ExecutionContext) -> AgentResponse:
        log.info(f"[FederatedAgent] Executing dual-stream dispatch for query: {ctx.query}")
        
        # Instantiate sub-agents
        analytics_agent = AnalyticalAgent()
        graph_agent = GraphAgent()
        
        # Execute concurrently or sequentially. Here we do sequentially for safety with DuckDB session.
        log.info("[FederatedAgent] -> Spawning Analytics Sub-Task")
        analytics_res = analytics_agent.execute(ctx)
        
        log.info("[FederatedAgent] -> Spawning Network Sub-Task")
        graph_res = graph_agent.execute(ctx)
        
        # Merge charts
        combined_charts = []
        if analytics_res.charts:
            combined_charts.extend(analytics_res.charts)
        if graph_res.charts:
            combined_charts.extend(graph_res.charts)
            
        # Synthesize answers using the orchestrator
        synthesis_prompt = f"""You are the Chief Intelligence Commander synthesizing a federated response.
The user asked: "{ctx.query}"

We dispatched this to two specialized sub-agents:

1. ANALYTICS AGENT REPORT:
{analytics_res.answer}

2. NETWORK AGENT REPORT:
{graph_res.answer}

Synthesize a single, cohesive, professional executive briefing that combines BOTH findings seamlessly.
Do NOT just paste them side by side. Weave the statistical data (caseloads, trajectories) together with the graph intelligence (mules, networks).
Use bolding for key entities and metrics.
"""
        
        synthesized_answer = orchestrator.generate_completion(
            prompt=synthesis_prompt,
            system_instruction="You are a senior KSP intelligence synthesizer.",
            max_tokens=2000
        )
        
        return AgentResponse(
            answer=synthesized_answer,
            agent_type="federated_agent",
            agent_label="KSP Federated Intelligence",
            agent_icon="🌐",
            agent_color="#a855f7",
            charts=combined_charts,
            executive_decision=analytics_res.executive_decision or graph_res.executive_decision,
            provider="groq",
            visuals_updated=analytics_res.visuals_updated or graph_res.visuals_updated,
            data_available=True,
            suggested_actions=["Review unified intelligence dossier", "Export federated report"]
        )
