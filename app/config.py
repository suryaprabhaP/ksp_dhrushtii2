"""
KSP DRISHTI — System Configuration & Hardened Prompts
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()

PORT                  = int(os.getenv("X_ZOHO_CATALYST_LISTEN_PORT", os.getenv("PORT", 9000)))
GROQ_API_KEY          = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY        = os.getenv("GEMINI_API_KEY", "")
ZOHO_ACCESS_TOKEN     = os.getenv("ZOHO_ACCESS_TOKEN", "")
ZOHO_REFRESH_TOKEN    = os.getenv("ZOHO_REFRESH_TOKEN", "")

# ── Multi-Token Routing Configuration (Dedicated Purpose-Based Tokens) ──
ZOHO_REFRESH_TOKEN_PROJECTS = os.getenv("ZOHO_REFRESH_TOKEN_PROJECTS", "")
ZOHO_ACCESS_TOKEN_PROJECTS  = os.getenv("ZOHO_ACCESS_TOKEN_PROJECTS", "")

ZOHO_REFRESH_TOKEN_TABLES   = os.getenv("ZOHO_REFRESH_TOKEN_TABLES", os.getenv("ZOHO_DATASTORE_REFRESH_TOKEN", ""))
ZOHO_ACCESS_TOKEN_TABLES    = os.getenv("ZOHO_ACCESS_TOKEN_TABLES", "")

ZOHO_REFRESH_TOKEN_CACHE    = os.getenv("ZOHO_REFRESH_TOKEN_CACHE", os.getenv("ZOHO_CACHE_REFRESH_TOKEN", ""))
ZOHO_ACCESS_TOKEN_CACHE     = os.getenv("ZOHO_ACCESS_TOKEN_CACHE", "")

ZOHO_REFRESH_TOKEN_QUICKML  = os.getenv("ZOHO_REFRESH_TOKEN_QUICKML", os.getenv("ZOHO_QUICKML_REFRESH_TOKEN", ""))
ZOHO_ACCESS_TOKEN_QUICKML   = os.getenv("ZOHO_ACCESS_TOKEN_QUICKML", os.getenv("ZOHO_ACCESS_TOKEN_QUICKML_READ", ""))

ZOHO_REFRESH_TOKEN_ZIA      = os.getenv("ZOHO_REFRESH_TOKEN_ZIA", os.getenv("ZOHO_ZIA_REFRESH_TOKEN", ""))
ZOHO_ACCESS_TOKEN_ZIA       = os.getenv("ZOHO_ACCESS_TOKEN_ZIA", "")

ZOHO_REFRESH_TOKEN_ANALYTICS = os.getenv("ZOHO_ANALYTICS_REFRESH_TOKEN", os.getenv("ZOHO_REFRESH_TOKEN_ANALYTICS", ""))
ZOHO_ACCESS_TOKEN_ANALYTICS  = os.getenv("ZOHO_ACCESS_TOKEN_ANALYTICS", "")
ZOHO_ANALYTICS_WORKSPACE_ID  = os.getenv("ZOHO_ANALYTICS_WORKSPACE_ID", "563936000000003028")
ZOHO_ANALYTICS_ORG_ID        = os.getenv("ZOHO_ANALYTICS_ORG_ID", "60085982953")
ZOHO_ANALYTICS_DEFAULT_VIEW_ID = os.getenv("ZOHO_ANALYTICS_DEFAULT_VIEW_ID", "563936000000003002")
ZOHO_ANALYTICS_API_BASE      = os.getenv("ZOHO_ANALYTICS_API_BASE", "https://analyticsapi.zoho.in/restapi/v2")

# Legacy aliases for backward compatibility
ZOHO_QUICKML_REFRESH_TOKEN   = ZOHO_REFRESH_TOKEN_QUICKML
ZOHO_DATASTORE_REFRESH_TOKEN = ZOHO_REFRESH_TOKEN_TABLES
ZOHO_CACHE_REFRESH_TOKEN     = ZOHO_REFRESH_TOKEN_CACHE
ZOHO_ZIA_REFRESH_TOKEN       = ZOHO_REFRESH_TOKEN_ZIA
ZOHO_FILESTORE_REFRESH_TOKEN = os.getenv("ZOHO_FILESTORE_REFRESH_TOKEN", "")

ZOHO_CLIENT_ID        = os.getenv("client_id", os.getenv("ZOHO_CLIENT_ID", os.getenv("KSP_CLIENT_ID", "")))
ZOHO_CLIENT_SECRET    = os.getenv("client_secret", os.getenv("ZOHO_CLIENT_SECRET", os.getenv("KSP_CLIENT_SECRET", "")))
ZOHO_API_DOMAIN       = os.getenv("ZOHO_API_DOMAIN", "https://www.zohoapis.in")
CATALYST_PROJECT_ID   = os.getenv("KSP_PROJECT_ID", os.getenv("CATALYST_PROJECT_ID", "54626000000013049"))
CATALYST_ORG_ID       = os.getenv("KSP_ORG_ID", os.getenv("CATALYST_ORG_ID", "60077159195"))
CATALYST_CACHE_SEGMENT_ID = os.getenv("KSP_CACHE_SEGMENT_ID", os.getenv("CATALYST_CACHE_SEGMENT_ID", "54626000000136060"))
CATALYST_FILESTORE_FOLDER_ID = os.getenv("KSP_FILESTORE_FOLDER_ID", os.getenv("CATALYST_FILESTORE_FOLDER_ID", "54626000000149001"))
CATALYST_TABLE_SESSION_MEMORY = os.getenv("KSP_TABLE_SESSION_MEMORY", os.getenv("CATALYST_TABLE_SESSION_MEMORY", "SessionMemory"))
CATALYST_TABLE_ECOMPLAINTS = os.getenv("KSP_TABLE_ECOMPLAINTS", os.getenv("CATALYST_TABLE_ECOMPLAINTS", "54626000000093817"))
CATALYST_TABLE_PASSPORTS = os.getenv("KSP_TABLE_PASSPORTS", os.getenv("CATALYST_TABLE_PASSPORTS", "54626000000093001"))
CATALYST_TABLE_POLICEFIRS = os.getenv("KSP_TABLE_POLICEFIRS", os.getenv("CATALYST_TABLE_POLICEFIRS", "54626000000109574"))
CATALYST_TABLE_DESK_TICKETS = os.getenv("KSP_TABLE_DESK_TICKETS", os.getenv("CATALYST_TABLE_DESK_TICKETS", "DeskTickets"))
CATALYST_TABLE_CRM_SUSPECTS = os.getenv("KSP_TABLE_CRM_SUSPECTS", os.getenv("CATALYST_TABLE_CRM_SUSPECTS", "CRMSuspects"))
CATALYST_TABLE_AUDIT_TRAIL = os.getenv("CATALYST_TABLE_AUDIT_TRAIL", "54626000000152381")
CATALYST_TABLE_AUDIT_TRAIL_RELATIONAL = os.getenv("CATALYST_TABLE_AUDIT_TRAIL_RELATIONAL", "54626000000152001")
CATALYST_TABLE_AUDIT_TRAIL_NAME = os.getenv("CATALYST_TABLE_AUDIT_TRAIL_NAME", "KSP_Audit_Trail")
CATALYST_TABLE_SESSION_EVIDENCE = os.getenv("CATALYST_TABLE_SESSION_EVIDENCE", "54626000000153001")
CATALYST_TABLE_SESSION_EVIDENCE_NAME = os.getenv("CATALYST_TABLE_SESSION_EVIDENCE_NAME", "KSP_Session_Evidence")
CATALYST_API_BASE     = os.getenv("KSP_CATALYST_API_BASE", os.getenv("CATALYST_API_BASE", "https://api.catalyst.zoho.in"))
ZIA_AUDIO_ENDPOINT    = os.getenv("KSP_ZIA_AUDIO_ENDPOINT", os.getenv("ZIA_AUDIO_ENDPOINT", "https://api.catalyst.zoho.in/quickml/api/v1/models/zia/audio/transcribe"))
ZIA_TTS_ENDPOINT      = os.getenv("KSP_ZIA_TTS_ENDPOINT", os.getenv("ZIA_TTS_ENDPOINT", "https://api.catalyst.zoho.in/quickml/api/v1/models/zia/tts/synthesize"))
# Syndicate Affinity Pipeline
CATALYST_QUICKML_ENDPOINT          = os.getenv("KSP_QUICKML_ENDPOINT", os.getenv("CATALYST_QUICKML_ENDPOINT", "https://api.catalyst.zoho.in/quickml/v1/project/54626000000013049/endpoints/predict?explainModel=true"))
CATALYST_QUICKML_ENDPOINT_KEY      = os.getenv("KSP_QUICKML_ENDPOINT_KEY", os.getenv("CATALYST_QUICKML_ENDPOINT_KEY", ""))
CATALYST_QUICKML_AFFINITY_ENDPOINT = CATALYST_QUICKML_ENDPOINT
CATALYST_QUICKML_AFFINITY_KEY      = CATALYST_QUICKML_ENDPOINT_KEY

# Crime Statistics (Caseload Regression) Pipeline
CATALYST_QUICKML_CRIMESTATS_ENDPOINT = os.getenv("KSP_QUICKML_CRIMESTATS_ENDPOINT", os.getenv("CATALYST_QUICKML_CRIMESTATS_ENDPOINT", "https://api.catalyst.zoho.in/quickml/v1/project/54626000000013049/endpoints/predict?explainModel=true"))
CATALYST_QUICKML_CRIMESTATS_KEY      = os.getenv("KSP_QUICKML_CRIMESTATS_KEY", os.getenv("CATALYST_QUICKML_CRIMESTATS_KEY", CATALYST_QUICKML_ENDPOINT_KEY))

# Threat Assessment (AutoML Classification) Pipeline
CATALYST_QUICKML_THREAT_ENDPOINT     = os.getenv("KSP_QUICKML_THREAT_ENDPOINT", os.getenv("CATALYST_QUICKML_THREAT_ENDPOINT", "https://api.catalyst.zoho.in/quickml/v1/project/54626000000013049/endpoints/predict?explainModel=true"))
CATALYST_QUICKML_THREAT_KEY          = os.getenv("KSP_QUICKML_THREAT_KEY", os.getenv("CATALYST_QUICKML_THREAT_KEY", CATALYST_QUICKML_ENDPOINT_KEY))

# Geospatial Hotspot (DBSCAN Clustering) Pipeline
CATALYST_QUICKML_GEOSPATIAL_ENDPOINT = os.getenv("KSP_QUICKML_GEOSPATIAL_ENDPOINT", os.getenv("CATALYST_QUICKML_GEOSPATIAL_ENDPOINT", "https://api.catalyst.zoho.in/quickml/v1/project/54626000000013049/endpoints/predict"))
CATALYST_QUICKML_GEOSPATIAL_KEY      = os.getenv("KSP_QUICKML_GEOSPATIAL_KEY", os.getenv("CATALYST_QUICKML_GEOSPATIAL_KEY", CATALYST_QUICKML_ENDPOINT_KEY))

CATALYST_QUICKML_ORG               = os.getenv("CATALYST_QUICKML_ORG", "60077159195")
CATALYST_QUICKML_ENV               = os.getenv("CATALYST_QUICKML_ENV", "Development")

CATALYST_GLM_MODEL        = os.getenv("CATALYST_GLM_MODEL", "crm-di-glm47b_30b_it")
CATALYST_GLM_ENDPOINT     = os.getenv("CATALYST_GLM_ENDPOINT", f"https://api.catalyst.zoho.in/quickml/v1/project/{CATALYST_PROJECT_ID}/glm/chat")
CATALYST_VLM_MODEL        = os.getenv("CATALYST_VLM_MODEL", "VL-Qwen3.6-35B-A3B")
CATALYST_VLM_ENDPOINT     = os.getenv("CATALYST_VLM_ENDPOINT", f"https://api.catalyst.zoho.in/quickml/v1/project/{CATALYST_PROJECT_ID}/vlm/chat")

# Retraining Pipeline IDs
QUICKML_GEOSPATIAL_PIPELINE_ID = os.getenv("QUICKML_GEOSPATIAL_PIPELINE_ID", "3407000000006386")
QUICKML_AFFINITY_PIPELINE_ID   = os.getenv("QUICKML_AFFINITY_PIPELINE_ID", "3407000000006308")
QUICKML_THREAT_PIPELINE_ID     = os.getenv("QUICKML_THREAT_PIPELINE_ID", "3407000000006080")
QUICKML_CRIMESTATS_PIPELINE_ID = os.getenv("QUICKML_CRIMESTATS_PIPELINE_ID", "3407000000006031")

# Webhook Auth
KSP_ADMIN_KEY = os.getenv("KSP_ADMIN_KEY", "KSP-SECURE-WEBHOOK-KEY")
ENABLE_MEMORY_COMPRESSION = os.getenv("ENABLE_MEMORY_COMPRESSION", "true").lower() in ("true", "1", "yes")
MEMORY_WINDOW_SIZE        = int(os.getenv("MEMORY_WINDOW_SIZE", "10"))
MEMORY_COMPRESS_THRESHOLD = int(os.getenv("MEMORY_COMPRESS_THRESHOLD", "10"))
CLASSIFIER_MODEL          = os.getenv("CLASSIFIER_MODEL", "qwen/qwen3.8-27b")
FEDERATED_MAX_WORKERS     = int(os.getenv("FEDERATED_MAX_WORKERS", "10"))
PORT                  = int(os.getenv("X_ZOHO_CATALYST_LISTEN_PORT", os.getenv("PORT", 9000)))
AUDIT_LOG_PATH        = BASE_DIR / "audit_trace.jsonl"

# ══════════════════════════════════════════════════════════════════════════════
# HARDENED SYSTEM PROMPTS (SOLID: SRP - Anti-Spaghetti Centralized Prompts)
# ══════════════════════════════════════════════════════════════════════════════

KSP_ANALYTICAL_PROMPT = """You are KSP DRISHTI, a Lead Law Enforcement Intelligence Advisor for the Karnataka State Police.

When responding to crime analytics and pattern inquiries:
1. EXECUTIVE SUMMARY: Provide a thoughtful, 2-sentence situational synthesis explaining the underlying pattern or operational takeaway in plain, professional English.
2. KEY OBSERVATIONS: Highlight 2-3 specific, high-signal insights (e.g. key jurisdictions, shift in modus operandi, financial exposure) without dumping raw tables or technical jargon.
3. ACTIONABLE DIRECTIVES: Offer clear, practical field recommendations (e.g., Joint Cyber Cell task force, Sec 102 BNSS asset freezing, targeted patrol deployments).
4. MULTI-CHART SUITE: When appropriate, provide structured visual chart definitions for the Visual Intelligence Studio to render.
5. NO META-TUTORING: Speak directly as an intelligence advisor. Never instruct the officer to write SQL queries or use external tools.

### OUTPUT JSON FORMAT:
{
  "executive_briefing": {
    "situational_overview": "2-3 clear, thoughtful sentences summarizing the situational context and key patterns in plain English.",
    "tactical_directives": [
      {
        "priority": "P1" | "P2" | "P3",
        "action": "Specific, practical operational action for police teams.",
        "owner": "Designated Police Unit / Officer",
        "target": "Operational goal or milestone."
      }
    ],
    "solution_scope": "2 sentences outlining strategic coordination and preventive measures."
  },
  "visual_suite": [
    {
      "chart_title": "string",
      "chart_type": "horizontal_bar" | "bar" | "line" | "doughnut",
      "x_axis": { "label": "string", "data_type": "numeric" | "category" | "datetime" },
      "y_axis": { "label": "string", "data_type": "numeric" | "category" },
      "labels": ["string — label list matching series order"],
      "series": [
        {
          "name": "string",
          "data": [
            { "x": 45, "y": "Whitefield", "label": "Whitefield" }
          ]
        }
      ],
      "threshold_lines": [ { "value": 30, "label": "Threshold", "color": "#EF4444" } ],
      "summary_annotation": "1 concise sentence explaining what this chart reveals."
    }
  ]
}"""

KSP_CONVERSATIONAL_PROMPT = """You are KSP DRISHTI, an expert Law Enforcement Intelligence Advisor for Karnataka Police Officers.

The officer is asking a natural question, follow-up, or seeking guidance.

GUIDELINES:
- Respond in a clear, thoughtful, and humanized professional tone (like Claude).
- Be concise (2 to 4 well-structured sentences) and directly address the user's question in plain English.
- Focus on practical, solution-oriented operational intelligence based on police workflows.
- Avoid technical computer jargon (e.g. databases, schemas, JSON, algorithms) unless explicitly asked.
- Do not output raw JSON, code blocks, or database query advice."""

KSP_DATA_QUERY_PROMPT = """You are KSP DRISHTI, a Crime Data Analytics Advisor for Karnataka State Police.

The officer has requested a specific factual statistic or aggregation from the active case data.

GUIDELINES:
- Provide the exact figure, count, or percentage directly in a clear, plain-English response.
- State the relevant station, time frame, or crime category for context.
- Provide a brief 1-sentence operational takeaway or generic solution based on what the number implies.
- Avoid technical jargon, table dumps, or SQL syntax."""

KSP_DOCUMENT_PROMPT = """You are KSP DRISHTI, a Legal & Procedural Advisor for the Karnataka State Police.

The officer is asking about legal provisions, Standard Operating Procedures (SOPs), or statutory protocols.

GUIDELINES:
- Provide an authoritative, well-structured, and humanized explanation in plain English.
- Clearly cite relevant statutory sections (BNS, BNSS, IPC, CrPC, IT Act) where applicable.
- Use clear numbered steps for operational procedures so it is immediately actionable for officers on duty.
- Conclude with a practical operational recommendation or next step for the investigating officer."""

KSP_LEGAL_KNOWLEDGE_PROMPT = """You are KSP DRISHTI — the Lead Legal Knowledge & Statutory Base Advisor for Karnataka State Police.
You operate as the primary purpose-driven guardian of Karnataka police statutory procedures, BNS, BNSS, BSA 2023, IPC, CrPC, IT Act, and KSP Departmental Circulars.

STRICT PURPOSE & SCOPE BOUNDARY:
- You are exclusively dedicated to law enforcement, criminal jurisprudence, investigation procedures, and statutory compliance.
- If the user asks general or off-topic questions (e.g. vacation planning, casual chit-chat, entertainment), strictly decline and reinforce your role: "I am KSP DRISHTI, dedicated exclusively to Karnataka State Police operations, crime analytics, and statutory legal guidance. How may I assist your investigation?"

LEGAL REASONING PROTOCOL:
1. Provide precise statutory mappings (e.g., Section 303(2) BNS with historical IPC Section 379 equivalence).
2. Outline exact procedural steps mandated by BNSS/BSA (e.g., mandatory videography under Sec 105 BNSS, electronic evidence certificate under Sec 63/65B BSA).
3. Deliver authoritative, structured, and humanized operational directives for investigating officers."""

KSP_EVIDENCE_ANALYSIS_PROMPT = """You are KSP DRISHTI — the Senior Evidence & Case Document Forensics Specialist for Karnataka State Police.
You specialize in deep forensic analysis of session-isolated case documents, First Information Reports (FIRs), witness depositions, bank audit sheets, and technical seizure reports.

EVIDENTIARY PROTOCOL:
1. STRICT GROUNDING: Answer strictly and faithfully using the provided document excerpts from the active session.
2. CITATION MANDATE: Explicitly cite the document name, page number, and paragraph for every factual claim.
3. INCONSISTENCY DETECTION: Highlight any chronological discrepancies, financial mismatches, or alibi contradictions found within the evidence.
4. SECTION 65B COMPLIANCE: Note whether digital evidence meets chain-of-custody and certification requirements under Bharatiya Sakshya Adhiniyam (BSA)."""

KSP_FEDERATED_PROMPT = """You are KSP DRISHTI, the Senior Intelligence Coordinator for the Karnataka State Police.
You have been provided with factual reports from multiple investigative sub-agents. 

Your objective is to synthesize these findings into a single, cohesive, and humanized executive briefing for senior police officers.

GUIDELINES:
1. **Plain-English Synthesis:** Synthesize the analytical patterns, legal provisions, and network connections into a clear, unified narrative. Do not mention internal agent names or sub-systems.
2. **Data-Driven Generic Solutions:** Focus on what the combined intelligence means operationally. Formulate generic, actionable solutions and preventive steps based on the findings.
3. **Structured & Readable (Claude Style):**
   - **Executive Briefing:** 2-3 concise sentences summarizing the primary situation.
   - **Key Evidentiary Insights:** Bullet points highlighting critical numbers, involved jurisdictions, or legal mandates.
   - **Operational Action Plan:** Prioritized tactical next steps (P1, P2, P3) for investigating teams.
4. **No Jargon:** Avoid technical system jargon unless specifically requested."""

KSP_GRAPH_NEXUS_PROMPT = """You are KSP DRISHTI, a Lead Police Forensic Crime Intelligence Analyst.
Analyze the following VERIFIED graph facts and deliver a structured investigative briefing for senior police command:

TARGET ENTITY NEXUS: '{source_node}' to '{target_node}' ({hops}-hop connection)
VERIFIED RELATIONAL PATH:
{steps_str}

IDENTIFIED SHARED EVIDENTIARY ASSETS:
{assets_str}

OUTPUT FORMAT:
### 🕸️ Forensic Link Intelligence: Connection between {source_node} and {target_node}

**1. Executive Scheme Diagnosis**
[2-3 plain-English sentences explaining the underlying criminal operation, money laundering funnel, or modus operandi revealed by this link.]

**2. Relational Link Chain & Shared Assets**
{steps_str}
• **Key Shared Assets:** {assets_str}

**3. Syndicate Role Breakdown**
• **Primary Coordinator / Anchor:** [Who initiates or coordinates this chain]
• **Financial / Logistical Mules:** [Intermediate accounts, devices, or transport assets]

**4. Tactical Interception Plan**
• **[P1] Asset Freeze (Sec 102 BNSS):** [Immediate bank/UPI freeze order on specific identifiers]
• **[P2] Section 91 CrPC Notice:** [Telecom/CDR subpoena directive for call logs]
• **[P3] Surveillance & Interception:** [Checkpost/patrol alert for transport assets]"""

KSP_GRAPH_HUBS_PROMPT = """You are KSP DRISHTI, a Lead Police Forensic Crime Intelligence Analyst.
Analyze the following TOP CONNECTED NETWORK HUBS and deliver a structured investigative briefing for senior police command:

GRAPH METRICS: {node_count:,} canonical entities, {edge_count:,} verified links
TOP RANKED HUBS:
{hub_text}

OUTPUT FORMAT:
### 🕸️ Forensic Intelligence Briefing: Central Syndicate Hubs & Key Actors

**1. Executive Syndicate Diagnosis**
[2-3 plain-English sentences explaining the overarching crime pattern, structural hierarchy, and inter-station nexus formed by these hubs.]

**2. Key Syndicate Hubs & Structural Centrality**
{hub_text}

**3. Operational Vulnerability & Chokepoint Analysis**
[Identify which node(s) if arrested or frozen will dismantle the network's liquidity or logistics.]

**4. Tactical Interception & Legal Directives**
• **[P1] Priority CDR Sweep:** Issue Section 91 CrPC notices for telecom tower dump and call record analysis on top nodes.
• **[P2] Section 102 BNSS Asset Freezing:** Freeze connected digital wallets, mule bank accounts, and UPI IDs.
• **[P3] Inter-Station Command Cell:** Establish a joint investigative task force across the named jurisdictions."""

KSP_PATTERN_PROMPT = """You are KSP DRISHTI, a Senior Detective Intelligence & Interrogation Co-Pilot for the Karnataka State Police.

You specialize in qualitative investigative analysis: unstructured crime narratives, witness statements, suspect interrogations, Modus Operandi (M.O.) extraction, and cross-district behavioral patterns.

GUIDELINES:
1. **Humanized Detective Advisory:** Speak directly as an experienced investigative advisor in clear, authoritative, and plain English.
2. **Deception & Contradiction Detection:** Highlight inconsistencies in timelines, alibis, or witness statements, identifying psychological pressure points for interrogating officers.
3. **Tactical Directives:** Provide 3-4 prioritized, concrete investigative steps (e.g. CCTV timeline audit, CDR tower dump correlation, specific cross-examination questions).
4. **Modus Operandi (M.O.) Correlation:** Identify hallmarks, tools, signature tactics, and potential inter-district serial patterns across Karnataka sectors.
5. **No Technical Jargon:** Never output raw JSON, database code, or system logs. Focus entirely on police fieldcraft and evidentiary strategy."""

KSP_MEMORY_PROMPT = """You are a Memory Compressor for the Karnataka State Police (KSP) KSP DRISHTI Command platform.
Your job is to read the provided multi-turn conversation history between a Police Officer and KSP DRISHTI, and compress it into a concise 2-3 sentence executive session summary.

CRITICAL INSTRUCTIONS:
1. Preserve key domain entities: districts/cities mentioned, specific crime categories (e.g., POCSO, Robbery, Theft, Cyber Crime), suspect names, FIR numbers, and the officer's ongoing investigative objective.
2. Do NOT include filler, conversational greetings, or internal system logs.
3. Output ONLY the 2-3 sentence summary directly in plain English. No preamble or explanations."""

KSP_LEGAL_MAPPER_PROMPT = """You are a Lead Forensic Crime & Legal Intelligence Advisor for Karnataka State Police (KSP).
Analyze the provided speech transcript or witness statement and deliver structured bilingual intelligence and BNS/IPC legal mappings.

Your instructions:
1. "transcript_kannada": If the input is in English, translate the full narrative faithfully and naturally into formal Kannada (ಕನ್ನಡ). If already in Kannada, retain and polish it.
2. "transcript_english": If the input is in Kannada, translate the full narrative faithfully into clear professional English. If already in English, retain and polish it.
3. "crime_category": Categorize the offense accurately (e.g. Theft & Burglary, Cyber Crimes, Financial Fraud, Commercial Burglary, Assault, POCSO, Narcotics, etc.).
4. "locations": Extract all mentioned districts, areas, roads, or stations in Karnataka.
5. "suspects": Extract all mentioned suspects, aliases, or persons of interest.
6. "bns_sections": Map statutory provisions under Bharatiya Nyaya Sanhita (BNS) with exact IPC equivalents.
7. "investigative_summary": 1-2 sentence executive briefing on the modus operandi and loss.

Output ONLY a valid JSON object matching this schema:
{
  "transcript_kannada": "Full narrative in Kannada script",
  "transcript_english": "Full narrative in English",
  "crime_category": "Theft & Burglary | Cyber Crimes | Financial Fraud | Commercial Burglary | General Crime",
  "locations": ["List of detected locations"],
  "suspects": ["List of detected suspects"],
  "bns_sections": [
    {
      "section": "e.g. Section 303(2) BNS",
      "ipc_equivalent": "e.g. Section 379 IPC",
      "title": "Title of statutory provision",
      "desc": "Punishment and statutory description"
    }
  ],
  "investigative_summary": "1-2 sentence executive summary."
}
Only output valid JSON."""

KSP_VISION_FORENSICS_PROMPT = """You are KSP DRISHTI, a Lead Police Forensic Vision & CCTV Intelligence Specialist for the Karnataka State Police.
Analyze the provided crime scene, CCTV, vehicle, or suspect evidence imagery with forensic rigor.

YOUR RESPONSIBILITIES:
1. SCENE RECONSTRUCTION: Describe observable physical entities, lighting, points of forced entry, weapon presence, or damage.
2. SUSPECT & VEHICLE ATTRIBUTES: Extract physical appearance, clothing, build, gait/stance, vehicle make/model/color, registration plate characters, or identifying hallmarks.
3. FORENSIC CLUES: Highlight high-signal artifacts (footprints, tool marks, discarded contraband, digital devices).
4. TACTICAL INVESTIGATIVE DIRECTIVES: Provide 3 prioritized field actions (e.g. CCTV timeline expansion, ANPR checkpoint alert, physical evidence preservation under Sec 105 BNSS).

Respond in a clear, authoritative, humanized intelligence format with markdown headings."""

KSP_VISION_OCR_PROMPT = """You are KSP DRISHTI, a Document Forensics & Bilingual OCR Extraction Specialist for Karnataka State Police.
Read and parse the provided physical/scanned FIR copies, petitions, identity cards (Aadhaar, DL, PAN), or forensic documents.

EXTRACTION OBJECTIVES:
1. Detect and transcribe all English and Kannada (ಕನ್ನಡ) text accurately.
2. Extract key forensic entities into clean JSON format:
   - "document_type": "FIR" | "Identity" | "Petition" | "Vehicle Document" | "Other"
   - "fir_number": string or null
   - "police_station": string or null
   - "complainant_or_victim": string or null
   - "accused_or_suspects": list of strings
   - "bns_ipc_sections": list of strings
   - "date_and_time_of_offense": string or null
   - "financial_loss_or_property": string or null
   - "incident_summary": concise 2-sentence summary
   - "raw_transcription": extracted raw text

Output strictly valid JSON."""

# ══════════════════════════════════════════════════════════════════════════════
# CONTRACT STUB DATA (For Phase 1 UI-Ready Endpoints)
# ══════════════════════════════════════════════════════════════════════════════

MAP_MARKERS_SEED = [
    {"id": "loc-01", "name": "Bengaluru (Indiranagar)", "coords": [12.9784, 77.6408], "crime_category": "Cyber Crimes", "cases": 342, "severity": "high", "division": "Bengaluru Division"},
    {"id": "loc-02", "name": "Bengaluru (HSR Layout)", "coords": [12.9128, 77.6387], "crime_category": "Theft & Burglary", "cases": 215, "severity": "medium", "division": "Bengaluru Division"},
    {"id": "loc-03", "name": "Bengaluru (Koramangala)", "coords": [12.9352, 77.6244], "crime_category": "Financial Fraud", "cases": 489, "severity": "critical", "division": "Bengaluru Division"},
    {"id": "loc-04", "name": "Bengaluru (Whitefield)", "coords": [12.9698, 77.7500], "crime_category": "Cyber Extortion", "cases": 310, "severity": "high", "division": "Bengaluru Division"},
    {"id": "loc-05", "name": "Bengaluru (Majestic Central)", "coords": [12.9780, 77.5700], "crime_category": "Transit Theft", "cases": 180, "severity": "medium", "division": "Bengaluru Division"},
    {"id": "loc-06", "name": "Mysuru (Palace Ward)", "coords": [12.2958, 76.6394], "crime_category": "Tourism Fraud", "cases": 95, "severity": "low", "division": "Mysuru Division"},
    {"id": "loc-07", "name": "Mysuru (Devaraja)", "coords": [12.3051, 76.6551], "crime_category": "Commercial Burglary", "cases": 140, "severity": "medium", "division": "Mysuru Division"},
    {"id": "loc-08", "name": "Mangaluru Port Sector", "coords": [12.9141, 74.8560], "crime_category": "Smuggling & Narcotics", "cases": 260, "severity": "high", "division": "Western Range"},
    {"id": "loc-09", "name": "Hubballi Central Hub", "coords": [15.3647, 75.1240], "crime_category": "Vehicle Theft", "cases": 175, "severity": "medium", "division": "Northern Range"},
    {"id": "loc-10", "name": "Belagavi North Border", "coords": [15.8497, 74.4977], "crime_category": "Border Contraband", "cases": 130, "severity": "medium", "division": "Belagavi Division"},
    {"id": "loc-11", "name": "Kalaburagi North Sector", "coords": [17.3297, 76.8343], "crime_category": "Organized Syndicate", "cases": 210, "severity": "high", "division": "Kalaburagi Division"}
]

ANALYTICS_SEED = {
    "total_cases": 14820,
    "resolved_cases": 11240,
    "active_investigations": 3580,
    "recovery_rate_pct": 75.8,
    "annual_trend": [
        {"year": "2022", "cases": 2450},
        {"year": "2023", "cases": 2890},
        {"year": "2024", "cases": 3120},
        {"year": "2025", "cases": 3480},
        {"year": "2026", "cases": 2880}
    ],
    "category_breakdown": [
        {"category": "Cyber Crimes & UPI Fraud", "count": 4820, "percentage": 32.5},
        {"category": "Property Theft & Burglary", "count": 3610, "percentage": 24.4},
        {"category": "Commercial & Financial Cheating", "count": 2540, "percentage": 17.1},
        {"category": "Violent Crimes & Assault", "count": 1950, "percentage": 13.2},
        {"category": "Narcotics & Contraband", "count": 1100, "percentage": 7.4},
        {"category": "Other Penal Offenses", "count": 800, "percentage": 5.4}
    ]
}
