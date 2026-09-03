import os
import sys
import json
import time

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server import app
from app.engine.session_store import session_store

client = app.test_client()

print("=" * 70)
print("TESTING CHATBOT DISPATCH -> ANALYTICAL AGENT")
print("=" * 70)

# SCENARIO 1: QuickML Caseload Prediction via Analytical Agent
print("\n--- [Scenario 1] Caseload Prediction Query ---")
query_1 = "Predict the caseload for ATM Gas Cutter Raids in September 2025"
payload_1 = {
    "query": query_1,
    "session_id": "test_analytics_session_01",
    "division": "Bengaluru Division"
}
t0 = time.time()
res1 = client.post("/chat", json=payload_1)
t1 = time.time()
print(f"Status: {res1.status_code} | Latency: {(t1 - t0):.3f}s")
data1 = res1.get_json() or {}
print(f"Agent Type: {data1.get('agent_type')}")
print(f"Agent Label: {data1.get('agent_label')}")
print(f"Provider: {data1.get('provider')}")
print(f"Answer Preview: {data1.get('answer', '')[:250]}...")
print(f"Charts Count: {len(data1.get('charts', []))}")
if data1.get("charts"):
    for idx, c in enumerate(data1["charts"]):
        print(f"  Chart {idx+1}: {c.get('title')} ({c.get('type')})")

# SCENARIO 2: Explicit Chart Query Without Attached Dataset (Guardrail Check)
print("\n--- [Scenario 2] Chart Query Without Dataset (Data Guard) ---")
query_2 = "Draw a bar chart of cybercrime vs burglary"
payload_2 = {
    "query": query_2,
    "session_id": "test_analytics_empty_session",
    "division": "Bengaluru Division"
}
t0 = time.time()
res2 = client.post("/chat", json=payload_2)
t1 = time.time()
print(f"Status: {res2.status_code} | Latency: {(t1 - t0):.3f}s")
data2 = res2.get_json() or {}
print(f"Agent Type: {data2.get('agent_type')}")
print(f"Provider: {data2.get('provider')}")
print(f"Answer: {data2.get('answer')}")

# SCENARIO 3: Direct '\analytics' slash command trigger
print("\n--- [Scenario 3] Direct '\\analytics' Slash Command ---")
query_3 = "\\analytics Compare financial loss across cyber fraud and robbery"
payload_3 = {
    "query": query_3,
    "session_id": "test_analytics_slash_session",
    "division": "Bengaluru Division"
}
t0 = time.time()
res3 = client.post("/chat", json=payload_3)
t1 = time.time()
print(f"Status: {res3.status_code} | Latency: {(t1 - t0):.3f}s")
data3 = res3.get_json() or {}
print(f"Agent Type: {data3.get('agent_type')}")
print(f"Agent Label: {data3.get('agent_label')}")
print(f"Provider: {data3.get('provider')}")
print(f"Answer Preview: {data3.get('answer', '')[:250]}...")

# SCENARIO 4: Analytics with Ingested Dataset in Session
print("\n--- [Scenario 4] Analytics with Ingested Session Dataset ---")
session_id_4 = "test_analytics_ingested_session"
csv_content = (
    "FIR_No,Station,Crime_Category,Loss_INR,Year\n"
    "FIR-001/2025,Indiranagar PS,Cyber Financial Fraud,150000,2025\n"
    "FIR-002/2025,Whitefield PS,Cyber Financial Fraud,420000,2025\n"
    "FIR-003/2025,Koramangala PS,Theft & Burglary,85000,2025\n"
    "FIR-004/2025,Indiranagar PS,Theft & Burglary,62000,2025\n"
    "FIR-005/2025,HSR Layout PS,Vehicle Theft,95000,2025\n"
    "FIR-006/2025,Whitefield PS,Commercial Cheating,890000,2025\n"
).encode("utf-8")

session_store.ingest_dataset(session_id_4, "ksp_crime_sample.csv", csv_content)

query_4 = "Analyze total financial loss and case count by crime category"
payload_4 = {
    "query": query_4,
    "session_id": session_id_4,
    "division": "Bengaluru Division"
}
t0 = time.time()
res4 = client.post("/chat", json=payload_4)
t1 = time.time()
print(f"Status: {res4.status_code} | Latency: {(t1 - t0):.3f}s")
data4 = res4.get_json() or {}
print(f"Agent Type: {data4.get('agent_type')}")
print(f"Agent Label: {data4.get('agent_label')}")
print(f"Provider: {data4.get('provider')}")
print(f"Answer Preview: {data4.get('answer', '')[:300]}...")
print(f"Charts Generated: {len(data4.get('charts', []))}")
if data4.get("charts"):
    for idx, c in enumerate(data4["charts"]):
        print(f"  Chart {idx+1}: {c.get('title')} ({c.get('type')})")
print(f"Executive Decision: {data4.get('executive_decision')}")

print("\n" + "=" * 70)
print("CHATBOT ANALYTICS AGENT EVALUATION COMPLETE")
print("=" * 70)
