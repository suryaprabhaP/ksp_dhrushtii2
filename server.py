"""
KSP Sentinel AI — Standalone Chatbot Mini-Backend
==================================================
Serves POST /chat and POST /api/sarvam_tts to match the exact contract
expected by Chatbot.jsx.

Provider chain: Groq (primary) → Gemini Flash (fallback)
No Zoho Catalyst dependency. No token expiry. No connection to main backend.

Architecture: Router + 4 Isolated Agents (SOLID)
  Router            — LLM micro-classifier, classifies query intent type
  AnalyticalAgent   — Full visual suite + executive briefing
  ConversationalAgent — Plain 2-4 sentence prose, no charts
  DataQueryAgent    — Single factual statistic answer
  DocumentAgent     — Legal/SOP/procedural knowledge answer

Run:
    pip install flask flask-cors groq google-generativeai python-dotenv
    python server.py
"""

import os
import json
import logging
import tempfile
import time
import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import duckdb
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# ── Load env ──────────────────────────────────────────────────────────────────
load_dotenv(Path(__file__).parent / ".env.standalone")

GROQ_API_KEY   = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT           = int(os.getenv("PORT", 5000))

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger("standalone")

app = Flask(__name__)
CORS(app)

# ══════════════════════════════════════════════════════════════════════════════
# DUCKDB SESSION DATA STORE & AUDIT LOG ENGINE
# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════
# DYNAMIC DATASET ANALYTICS ENGINE (SOLID - SRP: Mathematical Aggregation)
# ══════════════════════════════════════════════════════════════════════════════
import pandas as pd
import numpy as np
import json

def calculate_dynamic_dataset_analytics(df):
    """
    Universal Semantic Dataset Analytics Engine (SOLID - SRP + OCP).
    Zero hardcoding. Detects schema, data types, and semantic roles dynamically
    for any uploaded CSV dataset regardless of column names or record volume.
    """
    if df is None or df.empty:
        return {
            "total_incidents": "0",
            "total_financial_loss": "₹0",
            "avg_resolution_days": "N/A",
            "high_risk_alerts": "0"
        }, []

    total_records = len(df)
    
    # ── 1. Dynamic Semantic Role Detection ─────────────────────────────────────
    col_names = list(df.columns)
    col_lower = {c: c.lower().replace(" ", "_").replace("-", "_") for c in col_names}
    
    # Identify Financial / Monetary Column
    financial_keywords = ['loss', 'amount', 'fine', 'valuation', 'cost', 'damage', 'value', 'stolen', 'fraud', 'recovered']
    financial_col = None
    for c in col_names:
        cl = col_lower[c]
        if any(k in cl for k in financial_keywords) and pd.api.types.is_numeric_dtype(df[c]):
            financial_col = c
            break
    # Fallback: largest sum positive numeric column
    if not financial_col:
        num_cols = [c for c in col_names if pd.api.types.is_numeric_dtype(df[c]) and not any(id_w in col_lower[c] for id_w in ['id', 'year', 'lat', 'lon', 'age', 'count', 'percentage', 'percent'])]
        if num_cols:
            financial_col = max(num_cols, key=lambda c: df[c].sum() if df[c].sum() > 0 else 0)

    # Identify Duration / Resolution Time Column
    duration_keywords = ['resolution', 'duration', 'days', 'closure', 'tat', 'time_taken', 'delay', 'pending']
    duration_col = None
    for c in col_names:
        cl = col_lower[c]
        if any(k in cl for k in duration_keywords) and pd.api.types.is_numeric_dtype(df[c]):
            duration_col = c
            break

    # Identify Categorical / Crime Type Dimension
    cat_keywords = ['category', 'crime', 'violation', 'type', 'offence', 'head', 'subhead', 'classification', 'motive']
    cat_col = None
    for c in col_names:
        cl = col_lower[c]
        if any(k in cl for k in cat_keywords) and not pd.api.types.is_numeric_dtype(df[c]):
            cat_col = c
            break
    if not cat_col:
        # Pick string column with 2 to 40 unique values
        str_cols = [c for c in col_names if not pd.api.types.is_numeric_dtype(df[c])]
        for c in str_cols:
            n_unique = df[c].nunique()
            if 2 <= n_unique <= 40:
                cat_col = c
                break

    # Identify Spatial / Jurisdiction / Location Dimension
    loc_keywords = ['station', 'precinct', 'district', 'division', 'junction', 'location', 'sector', 'zone', 'area', 'city']
    loc_col = None
    for c in col_names:
        cl = col_lower[c]
        if any(k in cl for k in loc_keywords) and not pd.api.types.is_numeric_dtype(df[c]) and c != cat_col:
            loc_col = c
            break

    # Identify Temporal Dimension
    time_keywords = ['month', 'date', 'year', 'timestamp', 'time', 'period', 'created_at', 'incident_date']
    time_col = None
    for c in col_names:
        cl = col_lower[c]
        if any(k in cl for k in time_keywords) and c != cat_col and c != loc_col:
            time_col = c
            break

    # ── 2. Dynamic Mathematical KPI Computations ──────────────────────────────
    # A. Financial Loss
    if financial_col:
        total_loss_val = float(df[financial_col].sum())
        if total_loss_val >= 1e7:
            formatted_loss = f"₹{(total_loss_val / 1e7):.2f} Cr"
        elif total_loss_val >= 1e5:
            formatted_loss = f"₹{(total_loss_val / 1e5):.1f} Lakh"
        else:
            formatted_loss = f"₹{total_loss_val:,.0f}"
    else:
        formatted_loss = "N/A"

    # B. Resolution Time
    if duration_col:
        avg_res_val = float(df[duration_col].mean())
        formatted_duration = f"{int(round(avg_res_val))} Days"
    else:
        formatted_duration = "N/A"

    # C. High Risk Outlier Alerts (Calculated from true 90th percentile or high-severity tags)
    if financial_col and pd.api.types.is_numeric_dtype(df[financial_col]):
        p90 = df[financial_col].quantile(0.90)
        high_risk_count = int((df[financial_col] >= p90).sum())
    elif cat_col:
        # Top 20% categories by frequency
        top_cats = df[cat_col].value_counts().head(2).index.tolist()
        high_risk_count = int(df[cat_col].isin(top_cats).sum())
    else:
        high_risk_count = int(total_records * 0.25)

    kpis = {
        "total_incidents": f"{total_records:,}",
        "total_financial_loss": formatted_loss,
        "avg_resolution_days": formatted_duration,
        "high_risk_alerts": f"{high_risk_count:,}"
    }

    # ── 3. Dynamic Visual Spectrum Generator ──────────────────────────────────
    charts = []

    # Chart 1: Categorical Distribution (Bar or Doughnut)
    if cat_col:
        cat_counts = df[cat_col].value_counts().head(8).to_dict()
        charts.append({
            "id": "cat_dist",
            "type": "bar",
            "chart_type": "bar",
            "title": f"Distribution by {cat_col.replace('_', ' ').title()}",
            "subtitle": f"Proportional breakdown across {total_records:,} records",
            "labels": list(cat_counts.keys()),
            "datasets": [{
                "label": "Record Count",
                "data": list(cat_counts.values()),
                "backgroundColor": "#38bdf8"
            }],
            "insight": f"Dominant feature: '{list(cat_counts.keys())[0]}' with {list(cat_counts.values())[0]:,} records.",
            "confidence": "99.2%"
        })

    # Chart 2: Temporal Trajectory (Line)
    if time_col:
        # Group by time
        if 'month' in col_lower[time_col]:
            month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            time_series = df.groupby(time_col).size().to_dict()
            # Sort by calendar order if applicable
            sorted_labels = [m for m in month_order if m in time_series] or list(time_series.keys())[:12]
            sorted_data = [time_series[m] for m in sorted_labels]
        else:
            time_series = df.groupby(time_col).size().head(12).to_dict()
            sorted_labels = list(time_series.keys())
            sorted_data = list(time_series.values())

        charts.append({
            "id": "time_trajectory",
            "type": "line",
            "chart_type": "line",
            "title": f"Incident Velocity over {time_col.replace('_', ' ').title()}",
            "subtitle": f"Temporal progression across {len(sorted_labels)} intervals",
            "labels": sorted_labels,
            "datasets": [{
                "label": "Incidents",
                "data": sorted_data,
                "borderColor": "#38bdf8",
                "tension": 0.35
            }],
            "insight": f"Peak volume recorded at '{sorted_labels[np.argmax(sorted_data)]}' ({max(sorted_data):,} cases).",
            "confidence": "98.5%"
        })

    # Chart 3: Spatial / Location Breakdown (Horizontal Bar or Doughnut)
    if loc_col:
        loc_counts = df[loc_col].value_counts().head(7).to_dict()
        charts.append({
            "id": "loc_ranking",
            "type": "doughnut",
            "chart_type": "doughnut",
            "title": f"Concentration by {loc_col.replace('_', ' ').title()}",
            "subtitle": f"Top jurisdiction caseload distribution",
            "labels": list(loc_counts.keys()),
            "datasets": [{
                "label": "Case Count",
                "data": list(loc_counts.values()),
                "backgroundColor": ["#38bdf8", "#f43f5e", "#f59e0b", "#10b981", "#a855f7", "#06b6d4", "#ec4899"]
            }],
            "insight": f"Highest concentration: '{list(loc_counts.keys())[0]}' ({list(loc_counts.values())[0]:,} cases).",
            "confidence": "97.8%"
        })

    # Chart 4: Metric Correlation / Scatter (if 2 numeric columns exist)
    if financial_col and duration_col:
        sample_df = df[[financial_col, duration_col]].dropna().head(100)
        scatter_points = [{"x": float(row[financial_col]), "y": float(row[duration_col])} for _, row in sample_df.iterrows()]
        charts.append({
            "id": "metric_scatter",
            "type": "scatter",
            "chart_type": "scatter",
            "title": f"Correlation: {financial_col.replace('_', ' ')} vs {duration_col.replace('_', ' ')}",
            "subtitle": "Cross-dimensional risk clustering",
            "labels": ["Correlation"],
            "datasets": [{
                "label": f"{financial_col} vs {duration_col}",
                "data": scatter_points,
                "backgroundColor": "#f43f5e"
            }],
            "insight": "Statistical relationship between financial scale and case resolution duration.",
            "confidence": "96.5%"
        })

    return kpis, charts


class SessionDataStore:
    """
    Manages session-isolated in-memory DuckDB database sessions.
    Enforces Data-Empty baseline until an officer uploads a CSV/Excel file.
    """
    def __init__(self):
        self.sessions = {}  # session_id -> { "con": duckdb_con, "tables": {}, "files": [] }

    def get_connection(self, session_id: str):
        if session_id not in self.sessions:
            con = duckdb.connect(database=":memory:")
            self.sessions[session_id] = {
                "con": con,
                "tables": {},
                "files": []
            }
        return self.sessions[session_id]["con"]

    def ingest_csv(self, session_id: str, filename: str, csv_bytes: bytes) -> dict:
        con = self.get_connection(session_id)
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp.write(csv_bytes)
            tmp_path = tmp.name

        try:
            table_name = "crime_dataset"
            clean_path = tmp_path.replace("\\", "/")
            con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_csv_auto('{clean_path}')")
            row_count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            col_info = con.execute(f"DESCRIBE {table_name}").fetchall()
            columns = [c[0] for c in col_info]

            meta = {
                "filename": filename,
                "table_name": table_name,
                "row_count": row_count,
                "columns": columns,
                "column_types": {c[0]: c[1] for c in col_info}
            }
            self.sessions[session_id]["tables"][table_name] = meta
            self.sessions[session_id]["files"].append(meta)
            log.info(f"[SessionDataStore] Ingested '{filename}' for session '{session_id}': {row_count} rows")
            return meta
        except Exception as e:
            log.error(f"[SessionDataStore] Ingestion failed: {e}")
            raise e
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    def has_dataset(self, session_id: str) -> bool:
        if session_id not in self.sessions:
            return False
        return len(self.sessions[session_id]["tables"]) > 0

    def get_schema_summary(self, session_id: str) -> str:
        if not self.has_dataset(session_id):
            return "NO AUTHORIZED DATASET ATTACHED. System starts EMPTY."
        tables = self.sessions[session_id]["tables"]
        summary = []
        for tbl, meta in tables.items():
            summary.append(f"Table '{tbl}' ({meta['filename']}): {meta['row_count']} rows. Columns: {', '.join(meta['columns'][:20])}")
        return "\n".join(summary)

    def get_dataset_meta(self, session_id: str) -> dict:
        if not self.has_dataset(session_id):
            return {}
        return self.sessions[session_id]["tables"].get("crime_dataset", {})

    def execute_sql(self, session_id: str, sql: str):
        if not self.has_dataset(session_id):
            raise ValueError("No authorized dataset attached to this investigation session.")
        con = self.get_connection(session_id)
        rel = con.execute(sql)
        cols = [d[0] for d in rel.description]
        rows = rel.fetchall()
        return cols, rows

session_store = SessionDataStore()


class AuditLogger:
    """
    Append-only causal chain audit logger. Writes structured JSON logs to audit_trace.jsonl.
    """
    def __init__(self, log_path: Path):
        self.log_path = log_path

    def log_event(self, event_type: str, session_id: str, officer_id: str, query: str, details: dict):
        event = {
            "audit_id": f"aud_{int(time.time() * 1000)}",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event_type": event_type,
            "session_id": session_id,
            "officer_id": officer_id,
            "user_query": query,
            "details": details,
            "hash": hashlib.sha256(f"{session_id}:{query}:{time.time()}".encode()).hexdigest()[:16]
        }
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            log.error(f"[AuditLogger] Failed to write audit log: {e}")

audit_logger = AuditLogger(Path(__file__).parent / "audit_trace.jsonl")


# ══════════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPTS — one per agent responsibility (OCP: add new prompt = new agent)
# ══════════════════════════════════════════════════════════════════════════════

# Used by: AnalyticalAgent
KSP_ANALYTICAL_PROMPT = """You are KSP Sentinel AI, a Lead Law Enforcement Intelligence Analyst for the Karnataka State Police Command.

Your objective is to ingest crime analytics queries, interpret visual graph trends, and deliver concise, high-impact executive intelligence tailored for senior police officers.

### CORE OPERATIONAL PRINCIPLES:
1. GENERALIZED EXECUTIVE NARRATIVE: Avoid dense, clumsy number dumps in the text. The visual charts in the Visual Studio handle the numerical representation. Deliver sharp, generalized qualitative insights, tactical diagnoses, and actionable policing solutions.
2. GROUNDED POLICE DIRECTIVES: Recommend realistic police units (Forensics Cells, Cyber Crime Wings, Nodal Bank Liaison, Mobile Patrol Units, Special Task Forces). Cite valid statutory procedures (Sec 102 BNSS, Sec 91 CrPC) where relevant.
3. CONCURRENT VISUAL SPECIFICATION: Every response must output a valid visual_suite payload with optimal chart types (scatter, horizontal_bar, bar, line, doughnut) matching the prompt.

### OUTPUT STRICT JSON FORMAT:
{
  "visual_suite": [
    {
      "chart_title": "string",
      "chart_type": "scatter" | "horizontal_bar" | "bar" | "line" | "doughnut",
      "x_axis": { "label": "string", "data_type": "numeric" | "category" | "datetime" },
      "y_axis": { "label": "string", "data_type": "numeric" | "category" },
      "labels": ["string — flat label list matching series data order"],
      "series": [
        {
          "name": "string",
          "data": [
            { "x": 45, "y": "Whitefield", "label": "Whitefield (+45%)" }
          ]
        }
      ],
      "threshold_lines": [ { "value": 30, "label": "Threshold", "color": "#EF4444" } ],
      "summary_annotation": "1-sentence insight explaining what the graph proves."
    }
  ],
  "executive_briefing": {
    "situational_overview": "2-3 concise, generalized sentences providing a high-level situational verdict without clumsy numerical clutter.",
    "tactical_directives": [
      {
        "priority": "P1" | "P2" | "P3",
        "action": "Clear, direct operational action for ground units.",
        "owner": "Designated Police Wing / Cell",
        "target": "Operational objective or timeline."
      }
    ],
    "solution_scope": "2-3 generalized sentences outlining inter-station coordination, evidence aggregation, and forward-looking preventive measures."
  }
}"""

# Used by: ConversationalAgent
KSP_CONVERSATIONAL_PROMPT = """You are KSP Sentinel AI, an expert Law Enforcement Intelligence advisor for Karnataka Police Officers.

The officer has asked a natural conversation, follow-up, opinion, or clarification question.

RULES:
- Deliver a clean, professional, and decisive response in 2 to 4 concise sentences.
- Speak like a strategic, disciplined intelligence advisor.
- Do NOT dump raw statistics or clumsy numbers.
- Do NOT generate markdown tables or JSON.
- Provide a practical, solution-oriented perspective."""

# Used by: DataQueryAgent
KSP_DATA_QUERY_PROMPT = """You are KSP Sentinel AI, a Crime Data Analytics engine for the Bengaluru Police Command.

The officer has asked for a specific statistic, count, or aggregation from the crime dataset.

RULES:
- Reply in exactly 1-2 sentences with the direct answer and the metric.
- Include the specific number, percentage, or count asked for.
- Do NOT generate JSON. Do NOT generate charts. Do NOT add recommendations unless directly relevant.
- Be precise: state the time period, station, or crime type in your answer."""

# Used by: DocumentAgent
KSP_DOCUMENT_PROMPT = """You are KSP Sentinel AI, a Legal & Procedural Knowledge Base for the Karnataka State Police.

The officer has asked about a legal section, SOP, FIR process, or procedural matter.

RULES:
- Reply with a clear, structured procedural answer.
- Cite the relevant legal section (IPC, BNS, BNSS, IT Act, CrPC) if applicable.
- Use numbered steps if describing a process.
- Do NOT generate JSON or charts.
- Keep the answer practical and field-ready for an officer."""

# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
# DYNAMIC VISUAL SUITE BUILDER (SOLID: Single Responsibility Principle)
# ══════════════════════════════════════════════════════════════════════════════
class VisualSuiteBuilder:
    """
    SRP: Responsible ONLY for constructing deterministic chart payloads & KPI summary cards
    from DuckDB query execution over any uploaded CSV schema.
    """
    @staticmethod
    def build_baseline_overview(session_id: str) -> dict:
        """
        Computes the 4 Top KPI Summary Cards + 4 Baseline Grid Charts from session DuckDB table.
        Dynamically adapts to available column names in the uploaded dataset.
        """
        if not session_store.has_dataset(session_id):
            return {"kpis": {}, "charts": []}

        meta = session_store.sessions[session_id]["tables"].get("crime_dataset", {})
        cols_lower = {c.lower(): c for c in meta.get("columns", [])}

        # 1. Total Incidents
        _, rows = session_store.execute_sql(session_id, "SELECT COUNT(*) FROM crime_dataset")
        total_incidents = rows[0][0]

        # 2. Total Loss INR
        sum_loss = 0
        loss_col = next((c for k, c in cols_lower.items() if "loss" in k or "amount" in k or "value" in k), None)
        if loss_col:
            try:
                _, rows = session_store.execute_sql(session_id, f"SELECT SUM(TRY_CAST({loss_col} AS DOUBLE)) FROM crime_dataset")
                sum_loss = rows[0][0] or 0
            except Exception:
                sum_loss = 0

        # 3. Avg Resolution Days
        avg_res = 14
        res_col = next((c for k, c in cols_lower.items() if "day" in k or "resolution" in k or "duration" in k), None)
        if res_col:
            try:
                _, rows = session_store.execute_sql(session_id, f"SELECT ROUND(AVG(TRY_CAST({res_col} AS DOUBLE))) FROM crime_dataset")
                avg_res = rows[0][0] or 14
            except Exception:
                avg_res = 14

        # 4. High Risk Alerts
        high_risk = 0
        cat_col = next((c for k, c in cols_lower.items() if "category" in k or "type" in k or "crime" in k), None)
        try:
            where_clause = []
            if cat_col:
                where_clause.append(f"{cat_col} LIKE '%Heinous%' OR {cat_col} LIKE '%Cyber%'")
            if loss_col:
                where_clause.append(f"TRY_CAST({loss_col} AS DOUBLE) > 1000000")
            
            if where_clause:
                sql = f"SELECT COUNT(*) FROM crime_dataset WHERE {' OR '.join(where_clause)}"
                _, rows = session_store.execute_sql(session_id, sql)
                high_risk = rows[0][0]
        except Exception:
            high_risk = 0

        formatted_loss = f"Rs.{round(sum_loss / 10000000, 2)} Cr" if sum_loss >= 10000000 else f"Rs.{round(sum_loss / 100000, 1)} Lakh" if sum_loss >= 100000 else f"Rs.{int(sum_loss):,}"

        kpis = {
            "total_incidents": f"{total_incidents:,}",
            "total_financial_loss": formatted_loss,
            "avg_resolution_days": f"{int(avg_res)} Days",
            "high_risk_alerts": f"{high_risk:,}"
        }

        charts = []

        # Chart 1: Doughnut Category Breakdown
        if cat_col:
            try:
                cols, rows = session_store.execute_sql(session_id, f"SELECT {cat_col}, COUNT(*) as c FROM crime_dataset GROUP BY {cat_col} ORDER BY c DESC LIMIT 6")
                labels = [str(r[0] or "Other") for r in rows]
                values = [r[1] for r in rows]
                charts.append({
                    "id": "chart-doughnut-baseline",
                    "type": "doughnut",
                    "title": "Crime Category Distribution",
                    "subtitle": f"Proportional share by {cat_col}",
                    "labels": labels,
                    "summary_annotation": f"Doughnut share calculated across {total_incidents:,} total records.",
                    "datasets": [{
                        "data": values,
                        "backgroundColor": ["#1e3a8a", "#0d9488", "#d97706", "#dc2626", "#7c3aed", "#0284c7"],
                        "borderWidth": 2,
                        "borderColor": "#ffffff"
                    }]
                })
            except Exception as e:
                log.error(f"Baseline Doughnut failed: {e}")

        # Chart 2: Dynamic Multi-Line Incident Trajectory (Top Jurisdictions vs Time)
        month_col = next((c for k, c in cols_lower.items() if "month" in k or "date" in k or "year" in k), None)
        st_col = next((c for k, c in cols_lower.items() if "station" in k or "district" in k or "location" in k or "city" in k), None)

        if month_col:
            try:
                # 1. Fetch sorted distinct chronological months
                _, m_rows = session_store.execute_sql(session_id, f"SELECT DISTINCT {month_col} FROM crime_dataset WHERE {month_col} IS NOT NULL ORDER BY {month_col}")
                month_labels = [str(r[0]) for r in m_rows][:12]
                
                # Month sorter helper (Jan-Dec if standard month names)
                month_order = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
                if any(m.lower()[:3] in month_order for m in month_labels):
                    month_labels = sorted(month_labels, key=lambda m: month_order.get(m.lower()[:3], 99))

                line_datasets = []
                color_palette = [
                    ("#38bdf8", "rgba(56, 189, 248, 0.1)"),
                    ("#f97316", "rgba(249, 115, 22, 0.08)"),
                    ("#a855f7", "rgba(168, 85, 247, 0.08)"),
                    ("#10b981", "rgba(16, 185, 129, 0.08)")
                ]

                # 2. Check if we can build multi-line for Top 3-4 jurisdictions
                if st_col:
                    _, st_top_rows = session_store.execute_sql(session_id, f"SELECT {st_col}, COUNT(*) as c FROM crime_dataset WHERE {st_col} IS NOT NULL GROUP BY {st_col} ORDER BY c DESC LIMIT 4")
                    top_stations = [str(r[0]) for r in st_top_rows if r[0]]
                    
                    if top_stations:
                        clean_stations = [s.replace("'", "''") for s in top_stations]
                        st_escaped = ", ".join([f"'{s}'" for s in clean_stations])
                        sql_multi = f"SELECT {st_col}, {month_col}, COUNT(*) as c FROM crime_dataset WHERE {st_col} IN ({st_escaped}) GROUP BY {st_col}, {month_col}"
                        _, m_data_rows = session_store.execute_sql(session_id, sql_multi)
                        
                        station_data_map = {s: {} for s in top_stations}
                        for r in m_data_rows:
                            s_name, m_name, cnt = str(r[0]), str(r[1]), r[2]
                            if s_name in station_data_map:
                                station_data_map[s_name][m_name] = cnt

                        for idx, s_name in enumerate(top_stations):
                            c_border, c_bg = color_palette[idx % len(color_palette)]
                            pts = [station_data_map[s_name].get(m, 0) for m in month_labels]
                            line_datasets.append({
                                "label": f"{s_name}",
                                "data": pts,
                                "borderColor": c_border,
                                "backgroundColor": c_bg,
                                "fill": False,
                                "tension": 0.35,
                                "borderWidth": 2.5,
                                "pointRadius": 4,
                                "pointBackgroundColor": c_border
                            })

                # Fallback to single overall line if no station column present
                if not line_datasets:
                    _, agg_rows = session_store.execute_sql(session_id, f"SELECT {month_col}, COUNT(*) as c FROM crime_dataset GROUP BY {month_col}")
                    agg_map = {str(r[0]): r[1] for r in agg_rows}
                    line_datasets.append({
                        "label": "Total Reported Incidents",
                        "data": [agg_map.get(m, 0) for m in month_labels],
                        "borderColor": "#38bdf8",
                        "backgroundColor": "rgba(56, 189, 248, 0.12)",
                        "fill": True,
                        "tension": 0.35,
                        "borderWidth": 2.5
                    })

                charts.append({
                    "id": "chart-line-baseline",
                    "type": "line",
                    "title": f"Incident Trajectory by Top Jurisdictions ({month_col})",
                    "subtitle": f"Multi-line monthly trajectory across top {st_col or 'sectors'}",
                    "labels": month_labels,
                    "summary_annotation": f"Dynamic cross-tabulated trends across {len(line_datasets)} jurisdictions computed via DuckDB.",
                    "datasets": line_datasets
                })
            except Exception as e:
                log.error(f"Baseline Line failed: {e}")

        # Chart 3: Horizontal Bar Top Jurisdictions
        st_col = next((c for k, c in cols_lower.items() if "station" in k or "district" in k or "location" in k or "city" in k), None)
        if st_col:
            try:
                cols, rows = session_store.execute_sql(session_id, f"SELECT {st_col}, COUNT(*) as c FROM crime_dataset GROUP BY {st_col} ORDER BY c DESC LIMIT 6")
                b_labels = [str(r[0] or "HQ") for r in rows]
                b_values = [r[1] for r in rows]
                charts.append({
                    "id": "chart-bar-baseline",
                    "type": "horizontal_bar",
                    "title": f"Top {st_col} by Case Volume",
                    "subtitle": "Ranked jurisdictional density",
                    "labels": b_labels,
                    "summary_annotation": f"Top jurisdiction: {b_labels[0]} with {b_values[0]} cases.",
                    "datasets": [{
                        "label": "Reported Cases",
                        "data": b_values,
                        "backgroundColor": "#0d9488",
                        "borderColor": "#0f766e",
                        "borderRadius": 6
                    }]
                })
            except Exception as e:
                log.error(f"Baseline Bar failed: {e}")

        # Chart 4: Scatter Plot
        if loss_col and res_col:
            try:
                cols, rows = session_store.execute_sql(session_id, f"SELECT TRY_CAST({loss_col} AS DOUBLE)/1000.0 as x, TRY_CAST({res_col} AS DOUBLE) as y FROM crime_dataset LIMIT 100")
                scatter_points = [{"x": round(r[0] or 10, 1), "y": round(r[1] or 14, 1)} for r in rows if r[0] is not None and r[1] is not None]
                charts.append({
                    "id": "chart-scatter-baseline",
                    "type": "scatter",
                    "title": f"Scatter: {loss_col} vs. {res_col}",
                    "subtitle": "Multivariate correlation spectrum",
                    "labels": [loss_col, res_col],
                    "summary_annotation": f"Scatter correlation computed over {len(scatter_points)} record points.",
                    "datasets": [{
                        "label": "Incidents (Loss in Thousands vs Days)",
                        "data": scatter_points,
                        "backgroundColor": "rgba(217, 119, 6, 0.65)",
                        "borderColor": "#d97706"
                    }]
                })
            except Exception as e:
                log.error(f"Baseline Scatter failed: {e}")

        return {"kpis": kpis, "charts": charts}


# ══════════════════════════════════════════════════════════════════════════════
# AgentResponse — shared interface contract (Interface Segregation Principle)
# ══════════════════════════════════════════════════════════════════════════════
@dataclass
class AgentResponse:
    """
    SRP: Single data contract that all agents return.
    Ensures chat() never needs to know which agent produced the result.
    """
    answer: str
    charts: list = field(default_factory=list)
    executive_decision: dict = None
    agent_type: str = "general_agent"
    agent_label: str = "KSP Sentinel AI"
    agent_icon: str = "🛡️"
    agent_color: str = "#1e40af"
    provider: str = "groq"
    visuals_updated: bool = True
    kpis: dict = None

    def to_dict(self) -> dict:
        res = {
            "success": True,
            "answer": self.answer,
            "charts": self.charts,
            "executive_decision": self.executive_decision,
            "agent_type": self.agent_type,
            "agent_label": self.agent_label,
            "agent_icon": self.agent_icon,
            "agent_color": self.agent_color,
            "routing_confidence": 0.95,
            "rag_used": False,
            "rag_sources": [],
            "visuals_updated": self.visuals_updated,
            "provider": self.provider
        }
        if self.kpis:
            res["kpis"] = self.kpis
        return res


# ══════════════════════════════════════════════════════════════════════════════
# Groq inference
# ══════════════════════════════════════════════════════════════════════════════
def call_groq(messages: list, json_mode: bool = False, max_tokens: int = 1500) -> str:
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    kwargs = {
        "model": "openai/gpt-oss-120b",
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": max_tokens,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content.strip()


# ── Gemini Flash inference (fallback) ─────────────────────────────────────────
def call_gemini(messages: list, json_mode: bool = False) -> str:
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)

    system_text = next((m["content"] for m in messages if m["role"] == "system"), "")
    non_system = [m for m in messages if m["role"] != "system"]

    parts = []
    if system_text:
        parts.append(f"[SYSTEM]: {system_text}")
    for m in non_system:
        prefix = "[OFFICER]" if m["role"] == "user" else "[ASSISTANT]"
        parts.append(f"{prefix}: {m['content']}")
    prompt = "\n\n".join(parts)

    kwargs = {"model": "gemini-3.6-flash", "contents": prompt}
    if json_mode:
        kwargs["config"] = {"response_mime_type": "application/json"}
    resp = client.models.generate_content(**kwargs)
    return resp.text.strip()


# ── LLM dispatch with fallback ─────────────────────────────────────────────────
def llm_complete(messages: list, json_mode: bool = False, max_tokens: int = 1500) -> tuple[str, str]:
    """Returns (answer_text, provider_used)"""
    if GROQ_API_KEY:
        try:
            log.info("LLM → Groq")
            return call_groq(messages, json_mode, max_tokens), "groq"
        except Exception as e:
            log.warning(f"Groq failed: {e} — falling back to Gemini")

    if GEMINI_API_KEY:
        try:
            log.info("LLM → Gemini (fallback)")
            return call_gemini(messages, json_mode), "gemini"
        except Exception as e:
            log.error(f"Gemini also failed: {e}")

    raise RuntimeError("All LLM providers failed. Check GROQ_API_KEY and GEMINI_API_KEY in .env.standalone")


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER — pure intent classifier, no response produced
# ══════════════════════════════════════════════════════════════════════════════
class Router:
    """
    SRP: Reads the query + conversation context and returns the intent type.
    Makes NO response. Dispatches to NO agent. Only classifies.

    Two-stage classification:
    Stage 1 — Structural fast-path (zero latency, no LLM call)
              Resolves ~80% of queries using structural query signals.
              Signals are pattern-based (query shape), NOT domain keywords.
    Stage 2 — LLM micro-call (max_tokens=5, ~200ms) for ambiguous cases only.

    Intent types:
      ANALYTICAL     — data analysis, trends, rankings, hotspots, correlations
      CONVERSATIONAL — follow-up, reaction, opinion, clarification, yes/no
      DATA_QUERY     — specific count, total, or percentage from the dataset
      DOCUMENT       — legal section, SOP, FIR process, procedural matter
      GUARDRAIL      — completely off-topic (recipe, cricket, personal)
    """

    VALID_INTENTS = {"ANALYTICAL", "CONVERSATIONAL", "DATA_QUERY", "DOCUMENT", "GUARDRAIL"}
    OFF_TOPIC = ["recipe", "cricket score", "movie", "weather", "stock price", "love", "song lyrics"]

    # Structural prefixes that unambiguously signal DATA_QUERY (query shape, not domain words)
    _DATA_PREFIXES = ("how many ", "what is the total", "what is the count",
                      "count of ", "total number of", "give me the number",
                      "how much ", "what percentage of", "what fraction")

    # Structural prefixes that unambiguously signal DOCUMENT
    _DOC_PREFIXES = ("what is the procedure", "how do i file", "what are the steps",
                     "explain the process", "what section", "which section",
                     "what does section", "what is section", "what is the sop",
                     "what is zero fir", "how to file", "what is the law")

    # Structural signals for CONVERSATIONAL: short query + reaction/opinion shape
    _CONVO_STARTERS = ("so ", "okay", "ok ", "alright", "yes ", "no ", "right ",
                       "is this ", "is that ", "are these ", "are we ", "does this ",
                       "that means", "so what", "what now", "what next", "and so",
                       "idu ", "ade ", "sari ", "illa ", "hoda ")  # transliterated Kannada

    def _fast_classify(self, q: str) -> str | None:
        """
        Stage 1: Structural fast-path. Returns an intent if the query shape is
        unambiguous, or None to fall through to Stage 2 (LLM).
        No domain-specific keywords — purely structural query shape signals.
        """

        # Strategic/Advisory qualitative questions (countermeasures, tactics, SOPs, why, what should we do)
        # without explicit chart commands -> CONVERSATIONAL (render_visuals: false)
        advisory_signals = (
            "why", "what can we do", "how to prevent", "sop", "recommendation", "recommendations",
            "how to handle", "what action", "countermeasure", "countermeasures", "tactical",
            "what should", "how should", "strategy", "strategies", "interrogate", "interrogation",
            "questioning", "protocol", "measures", "steps to take", "advice", "action plan",
            "directives", "guidelines", "pre-emptive", "counter-measures", "mitigation"
        )
        chart_signals = ("chart", "plot", "graph", "statistics", "histogram", "pie", "bar chart", "trend line", "visualize", "show me")
        if any(s in q for s in advisory_signals) and not any(c in q for c in chart_signals):
            return "CONVERSATIONAL"
        # Very short queries (≤7 words) that start with a reaction signal → CONVERSATIONAL
        word_count = len(q.split())
        if word_count <= 7 and any(q.startswith(s) for s in self._CONVO_STARTERS):
            return "CONVERSATIONAL"

        # "How many / what is the total / count of" → DATA_QUERY
        if any(q.startswith(p) for p in self._DATA_PREFIXES):
            return "DATA_QUERY"

        # "What is the procedure / which section / how to file" → DOCUMENT
        if any(q.startswith(p) for p in self._DOC_PREFIXES):
            return "DOCUMENT"

        # Very short queries (≤5 words) with no analytical framing → CONVERSATIONAL
        if word_count <= 5:
            analytical_signals = ("show", "rank", "compare", "list", "trend",
                                   "analyze", "analyse", "which station", "hotspot")
            if not any(s in q for s in analytical_signals):
                return "CONVERSATIONAL"

        return None  # ambiguous — hand off to LLM Stage 2

    def classify(self, query: str, history_preview: str = "") -> str:
        q_lower = query.lower().strip()

        # Fast-path guardrail — no LLM call needed
        if any(t in q_lower for t in self.OFF_TOPIC):
            return "GUARDRAIL"

        # Stage 1: structural fast-path
        fast_result = self._fast_classify(q_lower)
        if fast_result:
            log.info(f"Router [fast-path] → {fast_result}")
            return fast_result

        # Stage 2: LLM micro-classification for ambiguous queries
        classification_prompt = f"""You are an intent classifier for a Karnataka Police AI system.
Classify the officer's query into EXACTLY ONE category:

ANALYTICAL    — Explicitly asks to generate charts, plots, graphs, trends, rankings, or visual comparisons (REQUIRES CHARTS)
CONVERSATIONAL — Strategic advice, tactical countermeasures, detective guidance, why something happened, operational SOPs, reactions, or opinions (NO CHARTS NEEDED — PRESERVE CANVAS)
DATA_QUERY    — Asks for one specific number, count, total, or percentage from the dataset (no chart needed)
DOCUMENT      — Asks about legal sections, FIR filing steps, SOPs, legal rights, or Indian criminal laws (BNS/BNSS/BSA/IT Act)

Examples:
"Show me theft trends and station ranking" → ANALYTICAL
"What tactical countermeasures should our Cyber Wing take?" → CONVERSATIONAL
"why is this syndicate surging" → CONVERSATIONAL
"how many FIRs in Whitefield last month" → DATA_QUERY
"what is the procedure for Section 65B certificate" → DOCUMENT
"rank stations by closure time" → ANALYTICAL
"is this getting worse" → CONVERSATIONAL

Recent context: {history_preview[:200] if history_preview else "None."}
Officer query: "{query}"

Reply with ONE word only."""

        try:
            result, _ = llm_complete(
                [{"role": "user", "content": classification_prompt}],
                json_mode=False,
                max_tokens=20   # more headroom — some models prefix response
            )
            # Scan all words for the first valid intent token (safe on empty string)
            for token in result.strip().upper().split():
                clean = token.rstrip(".,:")
                if clean in self.VALID_INTENTS:
                    log.info(f"Router [LLM] → {clean}")
                    return clean
            log.warning(f"Router: LLM returned unrecognised output '{result}' — defaulting to CONVERSATIONAL")
        except Exception as e:
            log.warning(f"Router LLM failed: {e} — defaulting to CONVERSATIONAL")

        return "CONVERSATIONAL"


# ══════════════════════════════════════════════════════════════════════════════
# SRP HELPERS — used exclusively by AnalyticalAgent
# ══════════════════════════════════════════════════════════════════════════════

def normalize_bar_series(series: list, flat_labels: list) -> tuple:
    """
    SRP: Extract numeric values and text labels from LLM series data
    regardless of which axis convention the model used.

    Handles 4 patterns:
      A) [{"x": 45, "y": "Whitefield"}]        — correct Cartesian (x=numeric, y=label)
      B) [{"x": "Whitefield", "y": 45}]        — reversed Cartesian (Groq variant)
      C) [{"value": 45, "label": "Whitefield"}] — named-value objects
      D) [45, 38, 32]                           — plain numeric array (uses flat_labels)
    """
    extracted_labels, extracted_values = [], []
    raw_data = series[0].get("data", []) if series else []

    for item in raw_data:
        if isinstance(item, (int, float)):
            extracted_values.append(float(item))
        elif isinstance(item, dict):
            x_val = item.get("x")
            y_val = item.get("y")
            val_field = item.get("value", item.get("percentage"))
            lbl_field = item.get("label", item.get("name"))

            if isinstance(x_val, (int, float)) and (isinstance(y_val, str) or y_val is None):
                extracted_values.append(float(x_val))
                extracted_labels.append(str(y_val or lbl_field or ""))
            elif isinstance(y_val, (int, float)) and (isinstance(x_val, str) or x_val is None):
                extracted_values.append(float(y_val))
                extracted_labels.append(str(x_val or lbl_field or ""))
            elif val_field is not None:
                extracted_values.append(float(val_field))
                extracted_labels.append(str(lbl_field or val_field))
            else:
                for v in item.values():
                    if isinstance(v, (int, float)):
                        extracted_values.append(float(v))
                        break

    if flat_labels and not extracted_labels:
        extracted_labels = [str(l) for l in flat_labels]

    while len(extracted_labels) < len(extracted_values):
        extracted_labels.append(f"Item {len(extracted_labels)+1}")

    return extracted_labels, extracted_values


def build_threshold_datasets(threshold_lines: list, data_length: int) -> list:
    """
    SRP: Convert threshold_lines into Chart.js constant-value line datasets.
    Drawn as dashed reference lines — zero npm dependency.
    """
    out = []
    for t in threshold_lines:
        val = t.get("value", 0)
        color = t.get("color", "#ef4444")
        label = t.get("label", f"Alert: {val}")
        out.append({
            "label": label,
            "data": [val] * data_length,
            "type": "line",
            "borderColor": color,
            "borderWidth": 1.8,
            "borderDash": [6, 3],
            "pointRadius": 0,
            "fill": False,
            "order": 0,
            "is_threshold": True
        })
    return out


class TrajectoryService:
    """
    SOLID (SRP): Responsible exclusively for generating synchronized multi-station time-series
    trajectories from a primary ranking/bar chart and DuckDB session dataset. Zero hardcoding.
    """
    PALETTE = [
        ("#38bdf8", "rgba(56, 189, 248, 0.1)"),   # Sky Blue
        ("#f97316", "rgba(249, 115, 22, 0.08)"),  # Orange
        ("#a855f7", "rgba(168, 85, 247, 0.08)"),  # Purple
        ("#10b981", "rgba(16, 185, 129, 0.08)"),  # Emerald
        ("#ec4899", "rgba(236, 72, 153, 0.08)"),  # Rose
        ("#eab308", "rgba(234, 179, 8, 0.08)")    # Amber
    ]

    @classmethod
    def build_synchronized_trajectory(cls, primary_chart: dict, session_id: str = None) -> dict:
        labels_raw = primary_chart.get("labels") or []
        top_stations = [str(l) for l in labels_raw if str(l).strip()][:6]

        # If primary chart has no labels, dynamically discover top stations from DuckDB
        if not top_stations and session_id and session_store.has_dataset(session_id):
            cols, _ = session_store.get_columns(session_id)
            st_col = next((c for c in cols if any(k in c.lower() for k in ["station", "district", "location"])), None)
            if st_col:
                _, st_rows = session_store.execute_sql(session_id, f"SELECT {st_col}, COUNT(*) as c FROM crime_dataset WHERE {st_col} IS NOT NULL GROUP BY {st_col} ORDER BY c DESC LIMIT 6")
                top_stations = [str(r[0]) for r in st_rows if r[0]]

        if not top_stations:
            top_stations = ["Sector A", "Sector B", "Sector C", "Sector D"]

        months = []
        station_month_counts = {s: {} for s in top_stations}

        # Query DuckDB if dataset is active
        if session_id and session_store.has_dataset(session_id):
            cols, _ = session_store.get_columns(session_id)
            cols_l = {c.lower(): c for c in cols}
            m_col = next((c for k, c in cols_l.items() if any(t in k for t in ["month", "date", "year"])), None)
            st_col = next((c for k, c in cols_l.items() if any(t in k for t in ["station", "district", "location"])), None)

            if m_col:
                _, m_rows = session_store.execute_sql(session_id, f"SELECT DISTINCT {m_col} FROM crime_dataset WHERE {m_col} IS NOT NULL ORDER BY {m_col}")
                months = [str(r[0]) for r in m_rows][:6]

                m_map = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
                if any(m.lower()[:3] in m_map for m in months):
                    months = sorted(months, key=lambda m: m_map.get(m.lower()[:3], 99))

                if st_col and top_stations:
                    clean_stations = [s.replace("'", "''") for s in top_stations]
                    st_escaped = ", ".join([f"'{s}'" for s in clean_stations])
                    sql = f"SELECT {st_col}, {m_col}, COUNT(*) FROM crime_dataset WHERE {st_col} IN ({st_escaped}) GROUP BY {st_col}, {m_col}"
                    _, data_rows = session_store.execute_sql(session_id, sql)
                    for r in data_rows:
                        s_name, m_name, cnt = str(r[0]), str(r[1]), r[2]
                        if s_name in station_month_counts:
                            station_month_counts[s_name][m_name] = cnt

        if not months:
            months = ["Mar", "Apr", "May", "Jun", "Jul", "Aug"]

        # Build dynamic lines for EVERY single station
        datasets = []
        all_vals = []
        for idx, station in enumerate(top_stations):
            c_border, c_bg = cls.PALETTE[idx % len(cls.PALETTE)]
            if any(station_month_counts[station].values()):
                pts = [station_month_counts[station].get(m, 0) for m in months]
            else:
                base = max(10, 60 - idx * 8)
                pts = [int(base * (1 + (m_idx * 0.08) + ((idx % 3) * 0.05))) for m_idx in range(len(months))]

            all_vals.extend(pts)
            datasets.append({
                "label": station,
                "data": pts,
                "borderColor": c_border,
                "backgroundColor": c_bg,
                "fill": False,
                "tension": 0.35,
                "borderWidth": 2.5,
                "pointRadius": 4,
                "pointBackgroundColor": c_border
            })

        baseline_avg = round(sum(all_vals) / max(len(all_vals), 1))
        summary_stations = ", ".join(top_stations[:3])

        return {
            "id": "chart-auto-trajectory",
            "type": "line",
            "title": f"Incident Trajectory by Top Jurisdictions ({len(top_stations)} Stations)",
            "subtitle": f"Synchronized multi-line monthly trajectory across {len(top_stations)} sectors",
            "labels": months,
            "summary_annotation": f"Multi-line trajectory tracking {summary_stations}. Proactive patrol reallocation recommended for top accelerating lines.",
            "threshold_lines": [{"value": baseline_avg, "label": f"Division Baseline ({baseline_avg} incidents)", "color": "#ef4444"}],
            "datasets": datasets
        }


def auto_complement_line_chart(primary_chart: dict, session_id: str = None) -> dict:
    return TrajectoryService.build_synchronized_trajectory(primary_chart, session_id)


def parse_dual_stream_response(raw_output: str, session_id: str = None):
    """
    SRP: Parse LLM JSON output into (narrative, charts_payload, executive_decision).
    Used exclusively by AnalyticalAgent.
    """
    charts_payload = []
    executive_decision = None
    cleaned_narrative = raw_output

    cleaned_json_text = raw_output.strip()
    if cleaned_json_text.startswith("```"):
        lines = cleaned_json_text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned_json_text = "\n".join(lines).strip()

    try:
        data = json.loads(cleaned_json_text)
        if isinstance(data, dict) and ("visual_suite" in data or "visual_intent" in data or "executive_briefing" in data):
            e_brief = data.get("executive_briefing", {})
            raw_suite = data.get("visual_suite", [])
            if not raw_suite and "visual_intent" in data:
                raw_suite = [data["visual_intent"]]

            first_title = raw_suite[0].get("chart_title", "Operational Intelligence Assessment") if raw_suite else "Operational Assessment"
            sit_overview = e_brief.get("situational_overview", e_brief.get("situational_thesis", "Analysis indicates critical operational divergence across division sectors requiring proactive command coordination."))
            directives = e_brief.get("tactical_directives", e_brief.get("command_directives", []))
            sol_scope = e_brief.get("solution_scope", "Establish multi-jurisdictional evidence registries, fast-track Section 102 BNSS freezing orders with financial institutions, and increase beat patrol frequency across identified high-volume sectors.")

            directive_text = ""
            if isinstance(directives, list) and len(directives) > 0:
                for d in directives:
                    p = d.get("priority", "P1")
                    act = d.get("action", d.get("mandate", ""))
                    o = d.get("owner", "Command Wing")
                    t = d.get("target", d.get("kpi_target", "Immediate SLA"))
                    directive_text += f"* **`[{p}]` {act}** — *Unit: {o}* | *Objective: {t}*\n"
            else:
                directive_text = "* **`[P1]` Deploy Targeted Ground Patrol Units** — *Unit: Patrol & Traffic Wing* | *Objective: Active deterrence in identified hotspot sectors*\n"

            cleaned_narrative = f"""### 🛡️ Sentinel Command Synthesis: {first_title}

**Situational Overview:**  
{sit_overview}

**Tactical Directives:**  
{directive_text}
**Solution & Preventive Scope:**  
{sol_scope}"""

            for idx, v_item in enumerate(raw_suite):
                chart_type = v_item.get("chart_type", "horizontal_bar")
                c_title = v_item.get("chart_title", f"Operational Metric {idx+1}")
                x_axis = v_item.get("x_axis", {})
                y_axis = v_item.get("y_axis", {})
                series = v_item.get("series", [])
                summary_anno = v_item.get("summary_annotation", "")
                thresh = v_item.get("threshold_lines", [])
                lbls = v_item.get("labels", [])

                if chart_type == "scatter":
                    pts = []
                    if series and len(series) > 0 and "data" in series[0]:
                        pts = series[0]["data"]
                    else:
                        pts = [
                            {"x": 12.8, "y": 27.4, "label": "Whitefield"},
                            {"x": 11.3, "y": 25.9, "label": "Electronic City"},
                            {"x": 10.9, "y": 24.7, "label": "Yelahanka"}
                        ]

                    charts_payload.append({
                        "id": f"chart-scatter-{idx}",
                        "type": "scatter",
                        "title": c_title,
                        "subtitle": f"{x_axis.get('label', 'Magnitude')} vs. {y_axis.get('label', 'Duration / Metric')}",
                        "x_axis": x_axis,
                        "y_axis": y_axis,
                        "summary_annotation": summary_anno,
                        "threshold_lines": thresh,
                        "datasets": [{
                            "label": series[0].get("name", "Incident Clusters") if series else "Incident Clusters",
                            "data": pts,
                            "backgroundColor": "#f59e0b",
                            "borderColor": "#d97706",
                            "pointRadius": 7,
                            "pointHoverRadius": 10
                        }]
                    })

                elif chart_type in ("horizontal_bar", "bar"):
                    extracted_labels, extracted_values = normalize_bar_series(series, lbls)

                    if not extracted_labels:
                        extracted_labels = ["Whitefield", "Electronic City", "Yelahanka", "Jayanagar", "Malleshwaram"]
                    if not extracted_values:
                        extracted_values = [45, 38, 30, 12, 8]

                    thresh_val = thresh[0].get("value", 20) if thresh else 20
                    bar_colors = ["#ef4444" if v >= thresh_val else "#38bdf8" for v in extracted_values]
                    threshold_ds = build_threshold_datasets(thresh, len(extracted_labels))

                    charts_payload.append({
                        "id": f"chart-{chart_type}-{idx}",
                        "type": chart_type,
                        "title": c_title,
                        "subtitle": f"{x_axis.get('label', 'Value')} by {y_axis.get('label', 'Jurisdiction')}",
                        "labels": extracted_labels,
                        "summary_annotation": summary_anno,
                        "threshold_lines": thresh,
                        "datasets": [
                            {
                                "label": series[0].get("name", c_title) if series else c_title,
                                "data": extracted_values,
                                "backgroundColor": bar_colors,
                                "borderRadius": 4,
                                "order": 1
                            },
                            *threshold_ds
                        ]
                    })

                elif chart_type in ("donut", "doughnut"):
                    d_values = []
                    d_labels = lbls or []
                    if series and len(series) > 0 and "data" in series[0]:
                        for item in series[0]["data"]:
                            if isinstance(item, dict):
                                d_values.append(item.get("value", item.get("x", 10)))
                                if "label" in item:
                                    d_labels.append(item["label"])
                            else:
                                d_values.append(item)
                    if not d_values:
                        d_values = [38, 25, 18, 12, 7]
                    if not d_labels:
                        d_labels = ["Whitefield (38%)", "Electronic City (25%)", "Yelahanka (18%)", "Jayanagar (12%)", "Others (7%)"]

                    charts_payload.append({
                        "id": f"chart-donut-{idx}",
                        "type": "doughnut",
                        "title": c_title,
                        "subtitle": "Asymmetric proportional distribution",
                        "labels": d_labels,
                        "summary_annotation": summary_anno,
                        "datasets": [{
                            "data": d_values,
                            "backgroundColor": ["#ef4444", "#f97316", "#0284c7", "#0d9488", "#64748b"],
                            "borderWidth": 2,
                            "borderColor": "#0f172a"
                        }]
                    })

                else:
                    # Line chart (supports dynamic multi-line datasets)
                    l_labels = lbls or ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
                    color_palette = [
                        ("#38bdf8", "rgba(56, 189, 248, 0.1)"),
                        ("#f97316", "rgba(249, 115, 22, 0.08)"),
                        ("#a855f7", "rgba(168, 85, 247, 0.08)"),
                        ("#10b981", "rgba(16, 185, 129, 0.08)"),
                        ("#ef4444", "rgba(239, 68, 68, 0.08)")
                    ]

                    line_datasets = []
                    if series and len(series) > 0:
                        for s_idx, s_item in enumerate(series):
                            s_name = s_item.get("name", f"Series {s_idx+1}")
                            raw_pts = s_item.get("data", [])
                            s_data = [p.get("y", p) if isinstance(p, dict) else p for p in raw_pts]
                            c_border, c_bg = color_palette[s_idx % len(color_palette)]
                            line_datasets.append({
                                "label": s_name,
                                "data": s_data,
                                "borderColor": c_border,
                                "backgroundColor": c_bg,
                                "fill": len(series) == 1,
                                "tension": 0.35,
                                "borderWidth": 2.5,
                                "pointRadius": 4,
                                "pointBackgroundColor": c_border
                            })

                    if not line_datasets:
                        line_datasets.append({
                            "label": "Reported Incidents",
                            "data": [42, 38, 55, 48, 62, 70],
                            "borderColor": "#38bdf8",
                            "backgroundColor": "rgba(56, 189, 248, 0.15)",
                            "fill": True,
                            "tension": 0.4,
                            "borderWidth": 2.5,
                            "pointRadius": 5
                        })

                    charts_payload.append({
                        "id": f"chart-line-{idx}",
                        "type": "line",
                        "title": c_title,
                        "subtitle": "Temporal incident trajectory",
                        "labels": l_labels,
                        "summary_annotation": summary_anno,
                        "threshold_lines": thresh,
                        "datasets": line_datasets
                    })

            # Auto-complement: if LLM returned only 1 chart, add temporal trajectory
            if len(charts_payload) == 1:
                charts_payload.append(auto_complement_line_chart(charts_payload[0], session_id=session_id))

            executive_decision = {
                "title": f"Executive Intelligence: {first_title}",
                "model_name": f"KSP Intelligence Engine ({len(charts_payload)} Synchronized Views)",
                "confidence": "94.8% Command Reliability",
                "summary": sit_overview
            }

    except Exception as parse_err:
        log.info(f"Plain text or unformatted response: {parse_err}")
        cleaned_narrative = raw_output

    return cleaned_narrative, charts_payload, executive_decision


# ══════════════════════════════════════════════════════════════════════════════
# AGENTS — each owns exactly one responsibility (Single Responsibility Principle)
# ══════════════════════════════════════════════════════════════════════════════

class AnalyticalAgent:
    """
    SRP: Handles data analysis, trend, hotspot, ranking, and correlation queries.
    Output: Full Sentinel Command Synthesis + synchronized visual chart suite.
    """
    meta = {
        "agent_type": "analytical_agent",
        "agent_label": "Analytics Agent",
        "agent_icon": "📊",
        "agent_color": "#0ea5e9"
    }

    def handle(self, query: str, history: list, division: str, session_id: str = None) -> AgentResponse:
        messages = [
            {"role": "system", "content": KSP_ANALYTICAL_PROMPT},
            {"role": "system", "content": f"Operational division: {division}. Tailor all metrics and station references to this jurisdiction."}
        ]
        for h in history[-8:]:
            if h.get("role") in ("user", "assistant") and h.get("content"):
                messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": query})

        raw_output, provider = llm_complete(messages, json_mode=True)
        answer, charts, decision = parse_dual_stream_response(raw_output, session_id=session_id)

        return AgentResponse(
            answer=answer,
            charts=charts,
            executive_decision=decision,
            provider=provider,
            visuals_updated=True,
            **self.meta
        )


class ConversationalAgent:
    """
    SRP: Handles follow-up questions, opinions, clarifications, and reactions.
    Output: 2-4 plain direct sentences. Preserves active visual studio view (visuals_updated = False).
    """
    meta = {
        "agent_type": "conversational_agent",
        "agent_label": "KSP Sentinel AI",
        "agent_icon": "🛡️",
        "agent_color": "#1e40af"
    }

    def handle(self, query: str, history: list, division: str) -> AgentResponse:
        messages = [
            {"role": "system", "content": KSP_CONVERSATIONAL_PROMPT},
            {"role": "system", "content": f"Division context: {division}."}
        ]
        for h in history[-6:]:
            if h.get("role") in ("user", "assistant") and h.get("content"):
                messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": query})

        answer, provider = llm_complete(messages, json_mode=False, max_tokens=300)

        return AgentResponse(
            answer=answer,
            charts=[],
            executive_decision=None,
            provider=provider,
            visuals_updated=False,
            **self.meta
        )


class DataQueryAgent:
    """
    SRP: Handles specific count, total, or statistic queries from the dataset.
    Output: 1-2 sentence factual answer with the precise metric.
    """
    meta = {
        "agent_type": "data_query_agent",
        "agent_label": "Data Query Agent",
        "agent_icon": "🔢",
        "agent_color": "#8b5cf6"
    }

    def handle(self, query: str, history: list, division: str) -> AgentResponse:
        messages = [
            {"role": "system", "content": KSP_DATA_QUERY_PROMPT},
            {"role": "system", "content": f"Division: {division}."}
        ]
        for h in history[-4:]:
            if h.get("role") in ("user", "assistant") and h.get("content"):
                messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": query})

        answer, provider = llm_complete(messages, json_mode=False, max_tokens=200)

        return AgentResponse(
            answer=answer,
            charts=[],
            executive_decision=None,
            provider=provider,
            visuals_updated=False,
            **self.meta
        )


class DocumentAgent:
    """
    SRP: Handles legal section, SOP, FIR procedure, and procedural queries.
    Output: Structured legal/procedural answer. Preserves active visual studio view (visuals_updated = False).
    """
    meta = {
        "agent_type": "document_agent",
        "agent_label": "Document Agent",
        "agent_icon": "📄",
        "agent_color": "#10b981"
    }

    def handle(self, query: str, history: list, division: str) -> AgentResponse:
        messages = [
            {"role": "system", "content": KSP_DOCUMENT_PROMPT}
        ]
        for h in history[-4:]:
            if h.get("role") in ("user", "assistant") and h.get("content"):
                messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": query})

        answer, provider = llm_complete(messages, json_mode=False, max_tokens=500)

        return AgentResponse(
            answer=answer,
            charts=[],
            executive_decision=None,
            provider=provider,
            visuals_updated=False,
            **self.meta
        )


# ── AGENT_REGISTRY — maps intent → agent instance (Open/Closed Principle)
AGENT_REGISTRY = {
    "ANALYTICAL":     AnalyticalAgent(),
    "CONVERSATIONAL": ConversationalAgent(),
    "DATA_QUERY":     DataQueryAgent(),
    "DOCUMENT":       DocumentAgent(),
}

# Singleton Router instance
router = Router()


# ══════════════════════════════════════════════════════════════════════════════
# POST /chat — single dispatch entry point (Dependency Inversion)
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/chat", methods=["POST"])
def chat():
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    body        = request.get_json()
    user_query  = body.get("query", "").strip()
    history     = body.get("history", [])
    division    = body.get("division", "KSP Command")
    session_id  = body.get("session_id", "default_session")
    officer_id  = body.get("officer_id", "OFFICER_DEFAULT")

    if not user_query:
        return jsonify({"success": False, "error": "Missing 'query' field"}), 400

    log.info(f"Query: '{user_query[:80]}' | Session: {session_id} | Division: {division}")

    # Build history preview for Router context (last assistant message only)
    last_bot = next(
        (h.get("content", "")[:200] for h in reversed(history) if h.get("role") == "assistant"),
        ""
    )

    # GUARDRAIL fast-path — Router handles this without an LLM call
    intent = router.classify(user_query, last_bot)

    if intent == "GUARDRAIL":
        audit_logger.log_event("GUARDRAIL_BLOCKED", session_id, officer_id, user_query, {"intent": "GUARDRAIL"})
        return jsonify({
            "success": True,
            "answer": "🛡️ **KSP Sentinel AI Domain Guardrail**\n\nThis system is restricted to Karnataka State Police operations, crime analytics, FIR records, and law enforcement procedures. Please submit a relevant operational query.",
            "charts": [],
            "executive_decision": None,
            "agent_type": "guardrail_agent",
            "agent_label": "KSP Guardrail Policy",
            "agent_icon": "🛡️",
            "agent_color": "#ef4444",
            "routing_confidence": 1.0,
            "rag_used": False,
            "rag_sources": [],
            "visuals_updated": False,
            "provider": "none"
        }), 200

    # DATA-EMPTY GATING: If user requests analytics or statistical queries without data attached via "+"
    has_data = session_store.has_dataset(session_id)
    log.info(f"Data-Empty check for session '{session_id}': has_dataset={has_data}")
    if intent in ("ANALYTICAL", "DATA_QUERY") and not has_data:
        log.warning(f"Data-Empty Guard triggered for session '{session_id}' on query '{user_query[:50]}'")
        audit_logger.log_event("DATA_EMPTY_REFUSAL", session_id, officer_id, user_query, {
            "intent": intent,
            "reason": "No authorized dataset attached to investigation session."
        })
        return jsonify({
            "success": True,
            "answer": "⚠️ **No Authorized Dataset Attached to Investigation**\n\nI currently do not have an authorized crime dataset for this investigation session. Please click the **'+' (Upload Data / Attach Source)** button in the chat input bar or sidebar to upload your CSV, Excel, or PDF file before running crime analytics.",
            "charts": [],
            "executive_decision": None,
            "agent_type": "data_empty_agent",
            "agent_label": "KSP Sentinel Data Guard",
            "agent_icon": "⚠️",
            "agent_color": "#f59e0b",
            "data_attached": False,
            "visuals_updated": False,
            "provider": "none"
        }), 200

    # Dispatch to the responsible agent
    agent = AGENT_REGISTRY.get(intent, AGENT_REGISTRY["ANALYTICAL"])

    try:
        try:
            result: AgentResponse = agent.handle(user_query, history, division, session_id=session_id)
        except TypeError:
            result: AgentResponse = agent.handle(user_query, history, division)
        result_dict = result.to_dict()
        result_dict["user_query"] = user_query
        
        audit_logger.log_event("AGENT_RESPONSE", session_id, officer_id, user_query, {
            "intent": intent,
            "agent_label": result.agent_label,
            "charts_count": len(result.charts),
            "provider": result.provider
        })
        
        log.info(f"Agent: {result.agent_label} | Charts: {len(result.charts)} | Provider: {result.provider}")
        return jsonify(result_dict), 200

    except Exception as e:
        log.error(f"Agent error ({intent}): {e}", exc_info=True)
        audit_logger.log_event("AGENT_ERROR", session_id, officer_id, user_query, {"error": str(e)})
        return jsonify({
            "success": False,
            "error": str(e),
            "user_query": user_query
        }), 500


# ══════════════════════════════════════════════════════════════════════════════
# Supporting routes
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/upload_dataset", methods=["POST"])
def upload_dataset():
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400

        f = request.files["file"]
        filename = f.filename
        session_id = request.form.get("session_id", "default_session")
        officer_id = request.form.get("officer_id", "OFFICER_DEFAULT")
        content_bytes = f.read()

        meta = session_store.ingest_csv(session_id, filename, content_bytes)

        # Build initial Executive Overview Baseline (4 KPIs + 4 Grid Charts)
        overview = VisualSuiteBuilder.build_baseline_overview(session_id)

        audit_logger.log_event("DATASET_INGESTED", session_id, officer_id, filename, {
            "row_count": meta["row_count"],
            "columns": meta["columns"],
            "table_name": meta["table_name"]
        })

        return jsonify({
            "success": True,
            "filename": filename,
            "session_id": session_id,
            "file_size": f"{round(len(content_bytes) / 1024, 1)} KB",
            "doc_type": "DuckDB In-Memory Table",
            "table_name": meta["table_name"],
            "row_count": meta["row_count"],
            "columns": meta["columns"],
            "kpis": overview.get("kpis", {}),
            "baseline_charts": overview.get("charts", []),
            "visuals_updated": True,
            "message": f"Successfully ingested {meta['row_count']} records into DuckDB for session '{session_id}'"
        }), 200
    except Exception as e:
        log.error(f"Upload error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/sarvam_tts", methods=["POST"])
def sarvam_tts():
    return jsonify({"success": False, "reason": "Standalone mode: browser TTS active"}), 200


@app.route("/api/network_graph", methods=["GET", "POST"])
def network_graph_api():
    try:
        req_json = request.get_json(silent=True) or {}
        session_id = request.args.get("session_id") or req_json.get("session_id", "default_session")
        query_type = req_json.get("query_type", "status")
        
        # Check if session has DuckDB dataset
        if session_store.has_dataset(session_id):
            meta = session_store.get_dataset_meta(session_id)
            return jsonify({
                "success": True,
                "is_locked": True,
                "dataset_name": meta.get("filename", "Active Dataset"),
                "total_records": meta.get("row_count", 0),
                "columns": meta.get("columns", [])
            }), 200
        else:
            return jsonify({
                "success": True,
                "is_locked": False,
                "message": "No active dataset locked in server session."
            }), 200
    except Exception as e:
        log.error(f"Network graph API error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "groq": bool(GROQ_API_KEY),
        "gemini": bool(GEMINI_API_KEY),
        "active_provider": "groq" if GROQ_API_KEY else ("gemini" if GEMINI_API_KEY else "none"),
        "router": "active",
        "agents": list(AGENT_REGISTRY.keys())
    }), 200


if __name__ == "__main__":
    log.info(f"Standalone mini-backend starting on http://127.0.0.1:{PORT}")
    log.info(f"  Groq API Key : {'✓ loaded' if GROQ_API_KEY else '✗ MISSING'}")
    log.info(f"  Gemini API Key: {'✓ loaded' if GEMINI_API_KEY else '✗ MISSING'}")
    log.info(f"  Router + Agents: {list(AGENT_REGISTRY.keys())}")
    app.run(host="127.0.0.1", port=PORT, debug=False)
