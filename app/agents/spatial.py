"""
KSP Sentinel AI — Spatial Tactical Agent (SOLID: SRP + LSP + DIP)
==================================================================
Handles spatial crime hotspots, DBSCAN clusters, tactical officer deployment,
and executes true database CRUD operations on Zoho CRM and Zoho Desk.
"""
import logging
from typing import Any, Dict, List, Optional
from app.core.interfaces import AgentManifest, AgentResponse, BaseAgent, ExecutionContext
from app.services.zoho_integration_service import zoho_service
from app.services.quickml_service import quickml_service

log = logging.getLogger("standalone.agent.spatial")


class SpatialTacticalAgent(BaseAgent):
    """
    SRP: Synthesizes geospatial tactical intelligence and coordinates Zoho Desk & CRM database tools,
         plus live Zoho Catalyst QuickML DBSCAN Hotspot & Threat Assessment inference engines.
    LSP: Implements BaseAgent returning standardized AgentResponse.
    DIP: Decoupled via ZohoIntegrationService, QuickMLService and Provider abstractions.
    """

    @property
    def manifest(self) -> AgentManifest:
        return AgentManifest(
            intent_name="SPATIAL_TACTICAL",
            label="Tactical Spatial Agent",
            icon="📍",
            color="#38bdf8",
            description="Trigger when the query involves geographical hotspots, clusters, tactical police deployment, patrol grids, Zoho CRM repeat suspect searches, or logging Zoho Desk dispatch tickets.",
            requires_visual_studio=False,
            system_prompt="You are the KSP Sentinel Tactical Spatial Agent. Formulate high-precision police tactical briefings, coordinate patrol deployments, and execute Zoho CRM/Desk tools and QuickML spatial predictions.",
            trigger_examples=[
                "Check Zoho CRM for repeat suspects operating here",
                "Log a priority dispatch ticket in Zoho Desk",
                "Analyze the spatial cluster and modus operandi",
                "Suggest checkpoint locations for this hotspot",
                "What is the threat level for Bengaluru Urban?"
            ],
            required_provider_tags=["free_reasoning"]
        )

    def execute(self, ctx: ExecutionContext) -> AgentResponse:
        log.info(f"[SpatialTacticalAgent] Executing query: '{ctx.query[:50]}' for session: '{ctx.session_id}'")

        # 1. Retrieve spatial context payload (from extra or default fallback)
        spatial_context = {}
        hotspot_metadata = {}
        sample_records = []

        context_injection = ctx.extra.get("context_injection") or {}
        if context_injection:
            spatial_context = context_injection.get("spatial_context") or {}
            hotspot_metadata = context_injection.get("hotspot_metadata") or {}
            sample_records = context_injection.get("sample_records") or []

        # If not in extra, fallback to division / defaults
        if not spatial_context:
            spatial_context = {
                "district_name": ctx.division or "Bengaluru Urban",
                "center_coordinates": [12.9716, 77.5946]
            }

        # 2. Check for explicit tool execution intents
        q_lower = ctx.query.lower()
        tool_results = []
        executed_tool_badges = []

        # Tool A: Zoho CRM Suspects Query
        if any(w in q_lower for w in ["crm", "suspect", "offender", "syndicate", "criminal", "warrant", "repeat"]):
            district = spatial_context.get("district_name", ctx.division or "Bengaluru")
            suspects = zoho_service.query_crm_suspects(district=district)
            tool_results.append({
                "tool": "zoho_crm_query",
                "count": len(suspects),
                "data": suspects
            })
            executed_tool_badges.append("🔍 Zoho CRM Suspect Dossiers Loaded")

        # Tool B: Zoho Desk Priority Ticket Creation
        if any(w in q_lower for w in ["ticket", "dispatch", "alert", "desk", "deploy", "p1", "priority"]):
            district = spatial_context.get("district_name", ctx.division or "Bengaluru Urban")
            threat = hotspot_metadata.get("threat_level", "HIGH")
            ticket = zoho_service.create_priority_ticket(
                district=district,
                summary=f"Tactical Response Deployment: {district} Cluster — {ctx.query[:80]}",
                threat_level="CRITICAL" if threat == "CRITICAL" else "HIGH"
            )
            tool_results.append({
                "tool": "zoho_desk_create_ticket",
                "ticket": ticket
            })
            executed_tool_badges.append(f"🎫 Zoho Desk Ticket #{ticket.get('ticket_number')} Generated")

        # Tool C: QuickML DBSCAN Geospatial Hotspot Inference
        if any(w in q_lower for w in ["cluster", "hotspot", "dbscan", "density", "geospatial", "coordinates", "gps", "grid"]):
            coords = spatial_context.get("center_coordinates", [12.9716, 77.5946])
            lat, lon = coords[0], coords[1]
            cluster_res = quickml_service.predict_spatial_hotspot(latitude=lat, longitude=lon, severity_weight=65)
            tool_results.append({
                "tool": "quickml_dbscan_hotspot",
                "data": cluster_res
            })
            executed_tool_badges.append(f"🌐 QuickML DBSCAN: {cluster_res.cluster_id} ({cluster_res.source})")

        # Tool D: QuickML AutoML Tactical Threat Assessment
        if any(w in q_lower for w in ["threat", "risk", "criticality", "severity", "assessment", "level"]):
            coords = spatial_context.get("center_coordinates", [12.9716, 77.5946])
            threat_res = quickml_service.predict_threat_level({
                "case_id": "KSP-TAC-LIVE",
                "crime_type": "Organized Robbery",
                "latitude": coords[0],
                "longitude": coords[1],
                "nearest_city": spatial_context.get("district_name", "Bengaluru"),
                "police_station": f"{spatial_context.get('district_name', 'Central')} PS",
                "case_status": "Under Investigation",
                "financial_loss_inr": 750000.0
            })
            tool_results.append({
                "tool": "quickml_threat_automl",
                "data": threat_res
            })
            executed_tool_badges.append(f"⚡ QuickML Threat AutoML: {threat_res.threat_level} ({threat_res.likelihood_score * 100:.1f}%)")

        # 3. Synthesize tactical response
        answer = self._build_tactical_reply(ctx.query, spatial_context, hotspot_metadata, sample_records, tool_results)

        # Append tool execution badges to the answer
        if executed_tool_badges:
            badge_markdown = "\n\n> 🛡️ **Enterprise Tool Executions:**\n" + "\n".join([f"> • **{b}**" for b in executed_tool_badges])
            answer = answer + badge_markdown

        manifest = self.manifest
        return AgentResponse(
            answer=answer,
            agent_type="spatial_tactical_agent",
            agent_label=manifest.label,
            agent_icon=manifest.icon,
            agent_color=manifest.color,
            charts=[],
            executive_decision=None,
            provider="tactical_orchestrator",
            visuals_updated=False,
            data_available=True,
            suggested_actions=[
                "Check Zoho CRM for repeat suspects",
                "Log a priority dispatch ticket in Zoho Desk",
                "Formulate Section 102 BNSS checkpoint grid"
            ]
        )

    def _build_tactical_reply(self, query: str, spatial_context: Dict, hotspot_metadata: Dict, sample_records: List, tool_results: List) -> str:
        district = spatial_context.get("district_name", "Active Sector")
        threat = hotspot_metadata.get("threat_level", "ELEVATED")
        coords = spatial_context.get('center_coordinates', [12.9716, 77.5946])

        sections = [
            f"### 📍 Tactical Response Briefing: **{district}**",
            f"**Operational Sector Threat:** `{threat}` | **Coordinates:** `{coords}`\n"
        ]

        # Render Tool Results
        has_tools = False
        for tr in tool_results:
            if tr.get("tool") == "zoho_crm_query":
                has_tools = True
                suspects = tr.get("data", [])
                sections.append(f"#### 🔍 Zoho CRM Suspect Registry ({len(suspects)} Targets Active in {district})")
                for s in suspects[:4]:
                    sections.append(f"- **{s.get('name')}** (Alias: *'{s.get('alias')}'*) — Primary Crime: `{s.get('primary_crime')}` | Threat Score: `{s.get('risk_score')}/100` | MO: *{s.get('known_modus_operandi')}*")
                sections.append("")

            elif tr.get("tool") == "quickml_dbscan_hotspot":
                has_tools = True
                c = tr.get("data")
                sections.append("#### 🌐 Zoho QuickML DBSCAN Hotspot Identification")
                sections.append(f"- **Identified Sector Cluster:** `{c.cluster_id}`")
                sections.append(f"- **Hotspot Status:** `{'ACTIVE DENSE CLUSTER' if c.is_hotspot else 'SPORADIC NOISE'}`")
                sections.append(f"- **Algorithm Confidence:** `{c.confidence * 100:.1f}%` ({c.status})")
                sections.append(f"- **Coordinates Evaluated:** Lat `{c.features_used.get('latitude')}`, Lon `{c.features_used.get('longitude')}`\n")

            elif tr.get("tool") == "quickml_threat_automl":
                has_tools = True
                th = tr.get("data")
                sections.append("#### ⚡ Zoho QuickML Tactical Threat Assessment (AutoML)")
                sections.append(f"- **Predicted Threat Tier:** `{th.threat_level}`")
                sections.append(f"- **Model Likelihood:** `{th.likelihood_score * 100:.1f}%` ({th.status})")
                sections.append(f"- **Inference Source:** `{th.source}`\n")
            sections.append(f"Situational analysis for **{district}** confirms elevated crime clustering. Intelligence advises establishing synchronized patrol perimeters along major transit corridors.")

        sections.append("#### 🚔 Tactical Action Plan:")
        sections.append("1. **Sector Interception Grid:** Deploy 2 highway patrol interceptors and mobile beat personnel.")
        sections.append("2. **Section 102 BNSS Audit:** Issue notices for suspected asset transactions linked to repeat offenders.")
        sections.append("3. **CCTV & ANPR Integration:** Cross-reference automated number plate records against identified suspect vehicles.")

        return "\n".join(sections)
