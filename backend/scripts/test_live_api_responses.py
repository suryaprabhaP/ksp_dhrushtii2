"""
Live End-to-End API Response Testing Suite
Tests all agent blueprints, dispatch workflows, suspect queries, and Chatbot interactions.
"""
import os
import sys
import json

# Ensure project root is on sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server import app
from app.services.zoho_integration_service import zoho_service


def test_api_responses():
    print("=" * 80)
    print("[START] RUNNING END-TO-END API RESPONSE VERIFICATION")
    print("=" * 80)

    client = app.test_client()

    # ──────────────────────────────────────────────────────────────────────────
    # 1. GET /api/investigation/suspects
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[ENDPOINT 1] GET /api/investigation/suspects?district=Bengaluru+Urban")
    resp = client.get("/api/investigation/suspects?district=Bengaluru+Urban")
    print(f"Status Code: {resp.status_code}")
    data = json.loads(resp.data.decode("utf-8"))
    print("Response JSON Payload:")
    print(json.dumps(data, indent=2))
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert data["success"] is True
    assert data["count"] > 0
    print("  -> Suspects Endpoint Verification: [PASS]")

    # ──────────────────────────────────────────────────────────────────────────
    # 2. POST /api/investigation/init
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[ENDPOINT 2] POST /api/investigation/init")
    init_payload = {
        "spatial_context": {
            "district_name": "Bengaluru Urban",
            "station": "Koramangala Police Station"
        },
        "hotspot_metadata": {
            "threat_level": "CRITICAL",
            "incident_count": 14,
            "primary_crimes": ["Chain Snatching", "Armed Robbery"]
        }
    }
    resp = client.post(
        "/api/investigation/init",
        data=json.dumps(init_payload),
        content_type="application/json"
    )
    print(f"Status Code: {resp.status_code}")
    init_data = json.loads(resp.data.decode("utf-8"))
    print("Response JSON Payload:")
    print(json.dumps(init_data, indent=2))
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}"
    assert init_data["success"] is True
    session_id = init_data["session_id"]
    print(f"  -> Investigation Session Initialized: {session_id} [PASS]")

    # ──────────────────────────────────────────────────────────────────────────
    # 3. POST /api/investigation/chat (Dispatch Trigger & Suspect Tool Execution)
    # ──────────────────────────────────────────────────────────────────────────
    print(f"\n[ENDPOINT 3] POST /api/investigation/chat (Session: {session_id})")
    chat_payload = {
        "session_id": session_id,
        "message": "Dispatch immediate Hoysala PCR backup and identify high risk suspects in this sector."
    }
    resp = client.post(
        "/api/investigation/chat",
        data=json.dumps(chat_payload),
        content_type="application/json"
    )
    print(f"Status Code: {resp.status_code}")
    chat_data = json.loads(resp.data.decode("utf-8"))
    print("Response JSON Payload (Truncated text):")
    print(json.dumps({
        "success": chat_data.get("success"),
        "session_id": chat_data.get("session_id"),
        "response_preview": chat_data.get("response", "")[:250] + "...",
        "tool_executions": chat_data.get("tool_executions", [])
    }, indent=2))
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert chat_data["success"] is True
    assert len(chat_data.get("tool_executions", [])) > 0
    print("  -> Investigation Agent Turn & Tool Execution: [PASS]")

    # ──────────────────────────────────────────────────────────────────────────
    # 4. GET /api/investigation/tickets
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[ENDPOINT 4] GET /api/investigation/tickets")
    resp = client.get("/api/investigation/tickets")
    print(f"Status Code: {resp.status_code}")
    tickets_data = json.loads(resp.data.decode("utf-8"))
    print("Response JSON Payload:")
    print(json.dumps(tickets_data, indent=2))
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert tickets_data["success"] is True
    assert tickets_data["count"] > 0
    print(f"  -> Live Dispatch Tickets Count: {tickets_data['count']} [PASS]")

    # ──────────────────────────────────────────────────────────────────────────
    # 5. POST /chat (Core Chatbot Polymorphic Dispatch)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[ENDPOINT 5] POST /chat (Polymorphic Chatbot Router)")
    post_chat_payload = {
        "query": "What are the latest spatial crime patterns in Bengaluru?",
        "session_id": "test_verification_session_001"
    }
    resp = client.post(
        "/chat",
        data=json.dumps(post_chat_payload),
        content_type="application/json"
    )
    print(f"Status Code: {resp.status_code}")
    main_chat_data = json.loads(resp.data.decode("utf-8"))
    print("Response JSON Payload Preview:")
    print(json.dumps({
        "agent_type": main_chat_data.get("agent_type"),
        "model_used": main_chat_data.get("model_used") or main_chat_data.get("provider"),
        "answer_preview": (main_chat_data.get("answer") or "")[:250] + "...",
        "has_charts": len(main_chat_data.get("charts", [])) > 0
    }, indent=2))
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert "answer" in main_chat_data or "text" in main_chat_data
    print(f"  -> Polymorphic /chat Response ({main_chat_data.get('agent_type')}) [PASS]")

    print("\n" + "=" * 80)
    print("[DONE] ALL ENDPOINT RESPONSES TESTED AND FULLY VALIDATED!")
    print("=" * 80)


if __name__ == "__main__":
    test_api_responses()
