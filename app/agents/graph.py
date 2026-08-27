"""
KSP Sentinel AI — Graph Intelligence Agent (SOLID: LSP + DIP)
Handles multi-hop link analysis, syndicate hub detection, and detective storytelling.
"""
import logging
import re
from typing import Dict, Any, List
from app.core.interfaces import BaseAgent, AgentManifest, ExecutionContext, AgentResponse
from app.engine.session_store import session_store
from app.engine.graph_engine import GraphEngine
from app.providers.orchestrator import orchestrator

log = logging.getLogger("standalone.agent.graph")

class GraphAgent(BaseAgent):
    """
    Graph Intelligence Agent.
    Implements deterministic BFS link traversal and neural forensic crime scheme interpretation.
    """

    @property
    def manifest(self) -> AgentManifest:
        return AgentManifest(
            intent_name="GRAPH",
            label="Graph Intelligence Agent",
            icon="🕸️",
            color="#0284c7",
            description="Deterministic Multi-Hop Graph Traversal & Forensic Link Analysis",
            requires_visual_studio=False,
            system_prompt="KSP Sentinel Graph Intelligence Agent for multi-hop link analysis and criminal scheme interpretation.",
            trigger_examples=[
                "Who are the central figures in our active cases?",
                "What is the connection between suspect A and suspect B?",
                "Trace the link path between vehicle KA04MB8812 and phone 9845012345"
            ]
        )

    def execute(self, ctx: ExecutionContext) -> AgentResponse:
        session_id = ctx.session_id
        user_query = ctx.query.strip()
        q_lower = user_query.lower()

        # ── 1. Ingest Data from Session Store into Graph Topology ─────────────
        if not session_id or not session_store.has_dataset(session_id):
            return AgentResponse(
                answer="### 🕸️ Graph Intelligence Active\n\nNo operational case dataset is currently loaded in memory. Please upload a crime records CSV or syndicate link ledger to enable relational intelligence.",
                agent_type="graph_intelligence_agent",
                agent_label=self.manifest.label,
                agent_icon=self.manifest.icon,
                agent_color=self.manifest.color,
                provider="graph_engine",
                visuals_updated=False,
                data_available=False
            )

        # Retrieve records across all active tables in DuckDB
        try:
            # Query primary or network dataset
            target_table = "network_dataset" if session_store.has_dataset(session_id, "network_dataset") else "crime_dataset"
            cols, rows = session_store.execute_sql(session_id, f"SELECT * FROM {target_table} LIMIT 10000")
            records = [dict(zip(cols, r)) for r in rows]
        except Exception as e:
            log.error(f"[GraphAgent] Failed to fetch session records: {e}")
            return AgentResponse(
                answer=f"### 🕸️ Graph Engine Error\n\nFailed to extract relational records from session `{session_id}`: {e}",
                agent_type="graph_intelligence_agent",
                agent_label=self.manifest.label,
                agent_icon=self.manifest.icon,
                agent_color=self.manifest.color,
                provider="graph_engine",
                visuals_updated=False,
                data_available=False
            )

        # Build In-Memory Graph Topology
        graph = GraphEngine.build_graph_from_records(records, cols)

        # ── 2. Shortest-Path / Nexus Query Handler ───────────────────────────
        path_match = re.search(r'(?:connection|nexus|link|path|relation(?:ship)?)\s+(?:between|from|of)\s+([\'\"]?[\w\s\-\.\+]+[\'\"]?)\s+(?:and|to)\s+([\'\"]?[\w\s\-\.\+]+[\'\"]?)', q_lower, re.I)
        if not path_match:
            path_match = re.search(r'how\s+is\s+([\'\"]?[\w\s\-\.\+]+[\'\"]?)\s+(?:connected|linked|related)\s+to\s+([\'\"]?[\w\s\-\.\+]+[\'\"]?)', q_lower, re.I)

        if path_match:
            ent_a = path_match.group(1).strip(" '\"?.,")
            ent_b = path_match.group(2).strip(" '\"?.,")

            path_res = GraphEngine.trace_shortest_path(graph, ent_a, ent_b)
            if path_res.get("found"):
                p_nodes = path_res["path_nodes"]
                p_edges = path_res["path_edges"]
                hops = path_res["hops"]

                # Extract verified factual steps
                steps = []
                shared_assets = []
                for idx, edge in enumerate(p_edges):
                    from_node = p_nodes[idx]
                    to_node = p_nodes[idx + 1]
                    rel_name = (edge.get("relation") or "LINKED_TO").replace("_", " ")
                    case_info = f" (Case Ref: {edge.get('caseRef')})" if edge.get('caseRef') else ""
                    steps.append(f"Step {idx + 1}: {from_node['label']} ({from_node['typeLabel']}) ➔ {to_node['label']} ({to_node['typeLabel']}){case_info}")
                    if to_node["type"] != "PERSON" and to_node["label"] not in [sa["label"] for sa in shared_assets]:
                        shared_assets.append(to_node)

                steps_str = "\n".join([f"• {s}" for s in steps])
                assets_str = ", ".join([f"{sa['typeLabel']} `{sa['label']}`" for sa in shared_assets]) or "None"

                # Synthesize Neural Forensic Intelligence Briefing via Orchestrator
                forensic_prompt = f"""You are KSP Sentinel AI, a Lead Police Forensic Crime Intelligence Analyst.
Analyze the following VERIFIED graph facts and deliver a structured investigative briefing for senior police command:

TARGET ENTITY NEXUS: '{p_nodes[0]['label']}' to '{p_nodes[-1]['label']}' ({hops}-hop connection)
VERIFIED RELATIONAL PATH:
{steps_str}

IDENTIFIED SHARED EVIDENTIARY ASSETS:
{assets_str}

OUTPUT FORMAT (Use this exact 4-tier structure):
### 🕸️ Forensic Link Intelligence: Connection between {p_nodes[0]['label']} and {p_nodes[-1]['label']}

**1. Executive Scheme Diagnosis**
[2-3 thoughtful sentences explaining the underlying criminal operation, money laundering funnel, or modus operandi revealed by this link.]

**2. Relational Link Chain & Shared Assets**
{steps_str}
• **Key Shared Assets:** {assets_str}

**3. Syndicate Role Breakdown**
• **Primary Coordinator / Anchor:** [Who initiates or coordinates this chain]
• **Financial / Logistical Mules:** [Intermediate accounts, devices, or transport assets]

**4. Tactical Interception Plan**
• **[P1] Asset Freeze (Sec 102 BNSS):** [Immediate bank/UPI freeze order on specific identifiers]
• **[P2] Section 91 CrPC Notice:** [Telecom/CDR subpoena directive for call logs]
• **[P3] Surveillance & Interception:** [Checkpost/patrol alert for transport assets]
"""
                try:
                    narrative = orchestrator.generate_completion(
                        forensic_prompt,
                        system_instruction="You are a Senior Police Intelligence Analyst. Provide clear, realistic, and legally sound forensic crime briefings."
                    )
                except Exception as e:
                    log.warning(f"[GraphAgent] Neural synthesis fallback: {e}")
                    narrative = f"""### 🕸️ Forensic Link Intelligence: {p_nodes[0]['label']} ➔ {p_nodes[-1]['label']}

**1. Executive Scheme Diagnosis**
A verified **{hops}-hop relational chain** connects **{p_nodes[0]['label']}** to **{p_nodes[-1]['label']}** through shared case records and inter-district syndicate assets.

**2. Relational Link Chain & Shared Assets**
{steps_str}
• **Key Shared Assets:** {assets_str}

**3. Syndicate Role Breakdown**
• **Primary Coordinator:** {p_nodes[0]['label']}
• **Intermediate Asset Layer:** {assets_str}

**4. Tactical Interception Plan**
• **[P1] Asset Freeze (Sec 102 BNSS):** Issue immediate freezing directives on all intermediate mule identifiers.
• **[P2] Section 91 CrPC Notice:** Subpoena telecom tower dump and activation logs for connected devices.
• **[P3] ANPR Surveillance:** Alert state highway toll checkposts for identified transport vehicles."""

                return AgentResponse(
                    answer=narrative,
                    agent_type="graph_intelligence_agent",
                    agent_label=self.manifest.label,
                    agent_icon=self.manifest.icon,
                    agent_color=self.manifest.color,
                    provider="graph_engine",
                    visuals_updated=False,
                    data_available=True
                )
            else:
                return AgentResponse(
                    answer=f"### 🕸️ Link Intelligence\n\n{path_res.get('reason', 'No direct or indirect connection found in the active case records.')}\n\n*Tip: Check the spelling of names, vehicle numbers, or phone identifiers.*",
                    agent_type="graph_intelligence_agent",
                    agent_label=self.manifest.label,
                    agent_icon=self.manifest.icon,
                    agent_color=self.manifest.color,
                    provider="graph_engine",
                    visuals_updated=False,
                    data_available=True
                )

        # ── 4. Syndicate Hubs / Central Figures Query ─────────────────────────
        if any(w in q_lower for w in ["central figure", "central figures", "syndicate hub", "syndicate hubs", "kingpin", "top connected", "hubs"]):
            god_nodes = graph.get("god_nodes", [])[:6]
            hub_bullets = []
            for i, n in enumerate(god_nodes):
                stn = n["metadata"].get("associatedStations", ["State HQ"])[0] if n["metadata"].get("associatedStations") else "General Sector"
                cases_count = len(n["metadata"].get("linkedCases", []))
                hub_bullets.append(f"{i + 1}. **{n['label']}** ({n['typeLabel']}) — {n['degree']} verified links across {cases_count} case files *(Jurisdiction: {stn})*")

            hub_text = "\n".join(hub_bullets)

            forensic_prompt = f"""You are KSP Sentinel AI, a Lead Police Forensic Crime Intelligence Analyst.
Analyze the following TOP CONNECTED NETWORK HUBS and deliver a structured investigative briefing for senior police command:

GRAPH METRICS: {graph['node_count']:,} canonical entities, {graph['edge_count']:,} verified links
TOP RANKED HUBS:
{hub_text}

OUTPUT FORMAT:
### 🕸️ Forensic Intelligence Briefing: Central Syndicate Hubs & Key Actors

**1. Executive Syndicate Diagnosis**
[2-3 sentences explaining the overarching crime pattern, structural hierarchy, and inter-station nexus formed by these hubs.]

**2. Key Syndicate Hubs & Structural Centrality**
{hub_text}

**3. Operational Vulnerability & Chokepoint Analysis**
[Identify which node(s) if arrested or frozen will dismantle the network's liquidity or logistics.]

**4. Tactical Interception & Legal Directives**
• **[P1] Priority CDR Sweep:** Issue Section 91 CrPC notices for telecom tower dump and call record analysis on top nodes.
• **[P2] Section 102 BNSS Asset Freezing:** Freeze connected digital wallets, mule bank accounts, and UPI IDs.
• **[P3] Inter-Station Command Cell:** Establish a joint investigative task force across the named jurisdictions.
"""
            try:
                narrative = orchestrator.generate_completion(
                    forensic_prompt,
                    system_instruction="You are a Senior Police Intelligence Analyst. Provide clear, realistic, and legally sound forensic crime briefings."
                )
            except Exception as e:
                log.warning(f"[GraphAgent] Hubs synthesis fallback: {e}")
                narrative = f"""### 🕸️ Central Figures & Network Hubs

Across **{graph['node_count']:,} indexed entities** and **{graph['edge_count']:,} cross-case links**, the following nodes hold the highest connectivity in the network:

{hub_text}

**Recommended Action Plan:**
• **[P1] Priority CDR Sweep:** Focus telecom tower dump and call detail record analysis on the top-ranked nodes.
• **[P2] Inter-Station Coordination:** Establish a joint investigative team across the primary police stations listed.
• **[P3] Financial Ledger Subpoena:** Issue Section 102 BNSS asset freezing orders on linked digital accounts and UPI IDs."""

            return AgentResponse(
                answer=narrative,
                agent_type="graph_intelligence_agent",
                agent_label=self.manifest.label,
                agent_icon=self.manifest.icon,
                agent_color=self.manifest.color,
                provider="graph_engine",
                visuals_updated=False,
                data_available=True
            )

        # ── 5. Entity Dossier Query ───────────────────────────────────────────
        dossier_match = re.search(r'(?:dossier|profile|who is|details|record)\s+(?:on|for|of)?\s*([\'\"]?[\w\s\-\.\+]+[\'\"]?)', q_lower, re.I)
        if dossier_match:
            ent_name = dossier_match.group(1).strip(" '\"?.,")
            d_res = GraphEngine.get_entity_dossier(graph, ent_name)
            if d_res.get("found"):
                node = d_res["node"]
                neighbors = d_res["direct_neighbors"][:8]
                assoc_text = "\n".join([f"• **{n['node']['typeLabel']}:** `{n['node']['label']}` *(Relationship: {n['relation']})*" for n in neighbors])

                narrative = f"""### 👤 Investigative Profile & Relational Dossier: `{node['label']}`

**Core Intelligence Summary:**
• **Entity Classification:** {node['typeLabel']}
• **Direct Relational Degree:** {node['degree']} verified cross-case linkages
• **Associated Case Files ({len(node['metadata'].get('linkedCases', []))}):** `{', '.join(node['metadata'].get('linkedCases', [])[:6])}`
• **Active Jurisdictions:** `{', '.join(node['metadata'].get('associatedStations', ['Central Command'])[:4])}`

**Primary Direct Associations:**
{assoc_text or '• No direct secondary associations recorded.'}

**Recommended Action Plan:**
• **[P1] Interrogation Subpoena:** Issue Section 91 CrPC notice for custodial cross-examination regarding linked assets.
• **[P2] Asset Scrutiny:** Flag financial accounts for forensic transaction tracing under Section 102 BNSS."""

                return AgentResponse(
                    answer=narrative,
                    agent_type="graph_intelligence_agent",
                    agent_label=self.manifest.label,
                    agent_icon=self.manifest.icon,
                    agent_color=self.manifest.color,
                    provider="graph_engine",
                    visuals_updated=False,
                    data_available=True
                )

        # Default Graph Summary
        return AgentResponse(
            answer=f"### 🕸️ Graph Intelligence Active\n\nThe relational network currently indexes **{graph['node_count']:,} canonical entities** and **{graph['edge_count']:,} cross-case edges**.\n\n*You can ask:*\n- *'Who are the central figures?'*\n- *'What is the connection between [Entity A] and [Entity B]?'*\n- *'Give me a dossier on [Suspect/Vehicle/Phone]'*",
            agent_type="graph_intelligence_agent",
            agent_label=self.manifest.label,
            agent_icon=self.manifest.icon,
            agent_color=self.manifest.color,
            provider="graph_engine",
            visuals_updated=False,
            data_available=True
        )
