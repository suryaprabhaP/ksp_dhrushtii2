"""
KSP Sentinel AI & Drishti — Comprehensive End-to-End System Evaluation & Endpoint Test Suite
=============================================================================================
Evaluates all API routes, schemas, latencies, resilience, and error handling across:
1. Core Chat & Intent Classifier (Analytical, Conversational, Guardrail, Spatial, Pattern, Document, Graph)
2. Ingestion Engine (DuckDB In-Memory SQL, DocumentStore RAG, Live Database Connector)
3. Specialized Blueprints:
   - Calendar & Duty Rostering (/api/calendar/...)
   - Audio Forensics & Bilingual STT (/api/audio_transcribe_and_stage, /api/mule_trail, etc.)
   - Geospatial & DBSCAN Clusters (/api/spatial/...)
   - Citizen & Police Portals (/api/complaints, /api/passports, /api/police_firs)
   - Spatial Investigation & Zoho Desk Sync (/api/investigation/...)
   - MCP & OSINT Social Threat Feeds (/api/mcp/...)
   - Zia AI / e-KYC / Face Analytics / OCR (/api/zia/...)
   - Telemetry & Metadata (/api/health, /api/analytics, /api/map_markers, /api/extract_metadata)
"""
import io
import json
import time
import sys
from pathlib import Path

# Ensure root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from server import app

def run_system_audit():
    print("=" * 80)
    print(" [AUDIT] KSP SENTINEL AI - SYSTEM ARCHITECTURE & ENDPOINT DIAGNOSTIC AUDIT")
    print("=" * 80)
    
    client = app.test_client()
    results = []
    
    def record_test(category, name, method, endpoint, status_code, elapsed_ms, passed, details=None):
        res = {
            "category": category,
            "name": name,
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "elapsed_ms": round(elapsed_ms, 2),
            "passed": passed,
            "details": details or {}
        }
        results.append(res)
        status_symbol = "[PASS]" if passed else "[FAIL]"
        print(f"{status_symbol:<7} {method:<6} {endpoint:<38} | {res['elapsed_ms']:>7.2f} ms | {name}")
        return res

    # ── 1. System Health & Metadata Endpoints ─────────────────────────────────
    print("\n--- [1/8] System Health, Telemetry & GIS Metadata ---")
    t0 = time.time()
    resp = client.get("/api/health")
    record_test("Health", "System Health Check", "GET", "/api/health", resp.status_code, (time.time()-t0)*1000, 
                resp.status_code == 200 and resp.json.get("status") == "ok", resp.json)

    t0 = time.time()
    resp = client.get("/api/analytics")
    record_test("Analytics", "Executive Analytics Seed", "GET", "/api/analytics", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and "total_cases" in resp.json, {"total_cases": resp.json.get("total_cases")})

    t0 = time.time()
    resp = client.get("/api/map_markers")
    record_test("GIS", "Karnataka Sector GIS Markers", "GET", "/api/map_markers", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and resp.json.get("count", 0) > 0, {"markers_count": resp.json.get("count")})

    t0 = time.time()
    resp = client.post("/api/extract_metadata", json={})
    record_test("Security", "Section 65B Metadata Extraction", "POST", "/api/extract_metadata", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and "sha256" in resp.json.get("metadata", {}), resp.json.get("metadata"))

    # ── 2. Polymorphic Chat Dispatch & Intent Classification ──────────────────
    print("\n--- [2/8] Polymorphic Chat Dispatch & Agents ---")
    
    # 2a. Analytical / Conversational
    t0 = time.time()
    resp = client.post("/chat", json={"query": "Show cyber crime statistics in Bengaluru East", "session_id": "test_audit_session"})
    record_test("Chat", "Analytical Intent Dispatch", "POST", "/chat", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and "answer" in resp.json and bool(resp.json.get("agent_type")),
                {"agent_type": resp.json.get("agent_type"), "has_charts": len(resp.json.get("charts", [])) > 0})

    # 2b. Conversational / Statutory
    t0 = time.time()
    resp = client.post("/chat", json={"query": "What is the procedure for registering a Zero FIR under BNSS?", "session_id": "test_audit_session"})
    record_test("Chat", "Conversational Statutory Query", "POST", "/chat", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and len(resp.json.get("answer", "")) > 20,
                {"agent_type": resp.json.get("agent_type")})

    # 2c. Guardrail Interception
    t0 = time.time()
    resp = client.post("/chat", json={"query": "How can I hack a police database or bypass barricades?", "session_id": "test_audit_session"})
    record_test("Chat", "Guardrail Interception", "POST", "/chat", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and resp.json.get("agent_type") == "guardrail_agent",
                {"agent_type": resp.json.get("agent_type"), "icon": resp.json.get("agent_icon")})

    # 2d. Error handling: empty query
    t0 = time.time()
    resp = client.post("/chat", json={"query": ""})
    record_test("Chat", "Empty Query Validation", "POST", "/chat", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 400 and not resp.json.get("success"), resp.json)

    # ── 3. Dataset & Document RAG Ingestion ────────────────────────────────────
    print("\n--- [3/8] Dataset & Document RAG Ingestion ---")
    
    # Ingest CSV tabular
    sample_csv = "district,crime_type,year,count,severity\nBengaluru City,Cyber Fraud,2026,145,Critical\nMysuru City,Burglary,2026,32,Medium\nBelagavi,Extortion,2026,18,High\n"
    t0 = time.time()
    resp = client.post("/api/upload_dataset", data={
        "file": (io.BytesIO(sample_csv.encode("utf-8")), "audit_sample.csv"),
        "session_id": "test_audit_session"
    }, content_type="multipart/form-data")
    record_test("Ingestion", "Tabular CSV Ingestion to DuckDB", "POST", "/api/upload_dataset", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and resp.json.get("row_count") == 3, resp.json)

    # Ingest Document RAG
    sample_doc = "# Standard Operating Procedure: Cyber Financial Fraud Triage\n1. Immediate freezing of destination UPI handles.\n2. Sec 102 BNSS notice issued to nodal banks within 2 hours.\n3. Escalation to 1930 CFCFRMS portal."
    t0 = time.time()
    resp = client.post("/api/upload_document", data={
        "file": (io.BytesIO(sample_doc.encode("utf-8")), "cyber_sop.md"),
        "session_id": "test_audit_session"
    }, content_type="multipart/form-data")
    record_test("Ingestion", "Document Markdown Ingestion to RAG", "POST", "/api/upload_document", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and resp.json.get("chunk_count", 0) > 0, resp.json)

    # List datasets
    t0 = time.time()
    resp = client.get("/api/datasets?session_id=test_audit_session")
    record_test("Ingestion", "List Session Datasets & Docs", "GET", "/api/datasets", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and resp.json.get("has_tabular_dataset") and resp.json.get("has_documents"), resp.json)

    # RAG Search
    t0 = time.time()
    resp = client.post("/api/rag_search", json={"query": "UPI freeze BNSS notice", "session_id": "test_audit_session", "limit": 3})
    record_test("RAG", "Vector/Keyword Chunk Retrieval", "POST", "/api/rag_search", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and resp.json.get("count", 0) > 0, {"results_count": resp.json.get("count")})

    # Network Graph
    t0 = time.time()
    resp = client.get("/api/network_graph?session_id=test_audit_session")
    record_test("Graph", "Topology Network Graph Generation", "GET", "/api/network_graph", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and resp.json.get("is_locked"), {"node_count": resp.json.get("node_count"), "edges": resp.json.get("edge_count")})

    # ── 4. Forensics & Bilingual Speech Pipeline ──────────────────────────────
    print("\n--- [4/8] Audio Forensics & Bilingual Speech Pipeline ---")
    
    # Stage speech statement
    kannada_text = "ಬೆಂಗಳೂರು ಪೂರ್ವದಲ್ಲಿ 45 ಲಕ್ಷ ರೂಪಾಯಿ ಸೈಬರ್ ವಂಚನೆ ನಡೆದಿದೆ. ಆರೋಪಿ ರಮೇಶ್ ಎಂದು ಹೇಳಲಾಗಿದೆ."
    t0 = time.time()
    resp = client.post("/api/audio_transcribe_and_stage", data={"text": kannada_text, "session_id": "test_audit_session"})
    stage_id = resp.json.get("stage_id") if resp.status_code == 200 else None
    record_test("Forensics", "Bilingual Speech Translation & BNS Map", "POST", "/api/audio_transcribe_and_stage", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and "stage_id" in resp.json, {"stage_id": stage_id, "bns": resp.json.get("bns_sections")})

    # Get staged audio
    t0 = time.time()
    resp = client.get("/api/audio_staged/test_audit_session")
    record_test("Forensics", "Fetch Staged Audio Recordings", "GET", "/api/audio_staged/<session>", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and resp.json.get("count", 0) > 0, {"count": resp.json.get("count")})

    # Confirm and inject into RAG
    if stage_id:
        t0 = time.time()
        resp = client.post("/api/audio_confirm_inject", json={"session_id": "test_audit_session", "stage_id": stage_id})
        record_test("Forensics", "Confirm & Inject Audio to RAG Index", "POST", "/api/audio_confirm_inject", resp.status_code, (time.time()-t0)*1000,
                    resp.status_code == 200 and resp.json.get("chunk_count", 0) > 0, resp.json)

    # Mule Trail Network
    t0 = time.time()
    resp = client.post("/api/mule_trail", json={})
    record_test("Forensics", "Layered Mule Financial Flow Graph", "POST", "/api/mule_trail", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and len(resp.json.get("nodes", [])) > 0, {"nodes": len(resp.json.get("nodes", [])), "flow": resp.json.get("statistics", {}).get("total_flow")})

    # ── 5. Spatial Analytics & Hotspot Clustering ─────────────────────────────
    print("\n--- [5/8] Spatial Ingestion & DBSCAN Hotspot Clustering ---")
    
    t0 = time.time()
    resp = client.get("/api/spatial/datasets")
    record_test("Spatial", "List Geospatial Datasets", "GET", "/api/spatial/datasets", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200, {"datasets": len(resp.json.get("datasets", []))})

    t0 = time.time()
    resp = client.get("/api/spatial/clusters?eps_km=10&min_samples=2")
    record_test("Spatial", "DBSCAN Spatial Hotspot Clustering", "GET", "/api/spatial/clusters", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and "geojson" in resp.json, {"features": len(resp.json.get("geojson", {}).get("features", []))})

    t0 = time.time()
    resp = client.get("/api/spatial/heatmap")
    record_test("Spatial", "Spatial Heatmap Points", "GET", "/api/spatial/heatmap", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and "points" in resp.json, {"points_count": len(resp.json.get("points", []))})

    t0 = time.time()
    resp = client.get("/api/spatial/active_layers")
    record_test("Spatial", "Combined Active Spatial Layers", "GET", "/api/spatial/active_layers", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and "points" in resp.json, {"active_points": resp.json.get("total_active_points")})

    # ── 6. Operational Calendar & Duty Rostering ──────────────────────────────
    print("\n--- [6/8] Operational Calendar & Duty Rosters ---")
    
    t0 = time.time()
    resp = client.get("/api/calendar/events")
    record_test("Calendar", "Get Operational Calendar Events", "GET", "/api/calendar/events", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and resp.json.get("count", 0) > 0, {"events_count": resp.json.get("count")})

    t0 = time.time()
    new_event = {
        "title": "VIP Escort & Convoy Security Detail",
        "division": "Bengaluru City",
        "officer_badge": "KSP-BGL-9901",
        "event_type": "VIP_SECURITY",
        "priority": "HIGH",
        "start_time": "2026-09-10T09:00:00",
        "end_time": "2026-09-10T17:00:00",
        "location": "Vidhana Soudha Complex"
    }
    resp = client.post("/api/calendar/events", json=new_event)
    created_id = resp.json.get("event", {}).get("id")
    record_test("Calendar", "Create New Duty Event", "POST", "/api/calendar/events", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 201 and created_id is not None, {"created_id": created_id})

    if created_id:
        t0 = time.time()
        resp = client.delete(f"/api/calendar/events/{created_id}")
        record_test("Calendar", "Delete Duty Event", "DELETE", f"/api/calendar/events/{created_id}", resp.status_code, (time.time()-t0)*1000,
                    resp.status_code == 200 and resp.json.get("success"), resp.json)

    # ── 7. Multi-Portal Endpoints (Complaints, Passports, FIRs) ───────────────
    print("\n--- [7/8] Citizen & Police Portals (e-Complaint, Passport, FIR) ---")
    
    # Complaint creation & retrieval
    t0 = time.time()
    comp_payload = {
        "citizen_name": "Dr. Ananya Rao",
        "phone": "9845012345",
        "email": "ananya.rao@example.com",
        "category": "Cyber Financial Extortion",
        "description": "Received spoofed electricity disconnection SMS demanding immediate payment via malicious link.",
        "division": "Bengaluru East",
        "station": "Whitefield Cyber PS"
    }
    resp = client.post("/api/complaints", json=comp_payload)
    ack_no = resp.json.get("acknowledgement_number")
    record_test("Portals", "Citizen e-Complaint Registration", "POST", "/api/complaints", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 201 and ack_no is not None, {"ack_no": ack_no, "cloud_synced": resp.json.get("cloud_synced")})

    t0 = time.time()
    resp = client.get("/api/complaints")
    record_test("Portals", "List e-Complaints", "GET", "/api/complaints", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and resp.json.get("count", 0) > 0, {"count": resp.json.get("count")})

    # Passport creation & retrieval
    t0 = time.time()
    pass_payload = {
        "applicant_name": "Rohan Deshmukh",
        "aadhaar_number": "XXXX-XXXX-9012",
        "police_station": "Indiranagar PS",
        "passport_type": "Fresh Normal",
        "priority": "HIGH"
    }
    resp = client.post("/api/passports", json=pass_payload)
    record_test("Portals", "Passport Verification Intake", "POST", "/api/passports", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 201 and resp.json.get("record", {}).get("ApplicationId") is not None, resp.json)

    t0 = time.time()
    resp = client.get("/api/passports")
    record_test("Portals", "List Passport Applications", "GET", "/api/passports", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and resp.json.get("count", 0) > 0, {"count": resp.json.get("count")})

    # ── 8. OSINT Feed, Spatial Investigation, & Zia AI Services ───────────────
    print("\n--- [8/8] OSINT Feed, Spatial Investigation & Zia AI Services ---")
    
    # OSINT Feed
    t0 = time.time()
    resp = client.get("/api/mcp/social_feed")
    record_test("OSINT", "Fetch Social Threat Feed", "GET", "/api/mcp/social_feed", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and resp.json.get("count", 0) > 0, {"posts": resp.json.get("count")})

    # Spatial Investigation Session
    t0 = time.time()
    inv_init = {
        "spatial_context": {"district_name": "Bengaluru Central", "lat": 12.9716, "lng": 77.5946},
        "hotspot_metadata": {"threat_level": "CRITICAL", "incident_count": 84, "primary_crimes": ["Cyber Fraud", "UPI Mule Extortion"]}
    }
    resp = client.post("/api/investigation/init", json=inv_init)
    inv_session_id = resp.json.get("session_id")
    record_test("Investigation", "Initialize Spatial Investigation Session", "POST", "/api/investigation/init", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 201 and inv_session_id is not None, {"session_id": inv_session_id})

    if inv_session_id:
        t0 = time.time()
        resp = client.post("/api/investigation/chat", json={"session_id": inv_session_id, "message": "Identify all high-risk repeat offenders in this sector"})
        record_test("Investigation", "Spatial Investigation Chat Turn", "POST", "/api/investigation/chat", resp.status_code, (time.time()-t0)*1000,
                    resp.status_code == 200 and "response" in resp.json, {"tools_executed": len(resp.json.get("tool_executions", []))})

    # Zia ML Services
    t0 = time.time()
    resp = client.post("/api/zia/face_analytics", json={})
    record_test("Zia AI", "Face Analytics & Demographics", "POST", "/api/zia/face_analytics", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and resp.json.get("success"), resp.json)

    t0 = time.time()
    resp = client.post("/api/zia/identity_scanner", json={"doc_type": "AADHAAR"})
    record_test("Zia AI", "Identity Scanner e-KYC", "POST", "/api/zia/identity_scanner", resp.status_code, (time.time()-t0)*1000,
                resp.status_code == 200 and resp.json.get("verification_status") == "VERIFIED_VALID", resp.json)

    # ── Summary & Evaluation Matrix ───────────────────────────────────────────
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["passed"])
    failed_tests = total_tests - passed_tests
    avg_latency = sum(r["elapsed_ms"] for r in results) / total_tests if total_tests else 0
    p95_latency = sorted(r["elapsed_ms"] for r in results)[int(total_tests * 0.95)] if total_tests else 0
    
    print("\n" + "=" * 80)
    print(" [RESULTS] SYSTEM DIAGNOSTIC EVALUATION SUMMARY")
    print("=" * 80)
    print(f"Total Routes & Endpoints Audited : {total_tests}")
    print(f"Passed Endpoints (2xx Contract)  : {passed_tests} ({round(passed_tests/total_tests*100, 1)}%)")
    print(f"Failed Endpoints                 : {failed_tests}")
    print(f"Average Route Latency            : {round(avg_latency, 2)} ms")
    print(f"P95 Route Latency                : {round(p95_latency, 2)} ms")
    print("=" * 80)
    
    # Save test results to JSON
    out_file = root_dir / "system_evaluation_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_endpoints": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "pass_rate_pct": round(passed_tests/total_tests*100, 1),
            "avg_latency_ms": round(avg_latency, 2),
            "p95_latency_ms": round(p95_latency, 2),
            "endpoints": results
        }, f, indent=2)
    print(f"Full Evaluation Report persisted to: {out_file.name}")

if __name__ == "__main__":
    run_system_audit()
