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

client = app.test_client()

print("=" * 75)
print("RUNNING LIVE TEST: SCENARIO 1 (CHATBOT -> ANALYTICAL AGENT -> ZOHO LLM)")
print("=" * 75)

query = "Predict the caseload for ATM Gas Cutter Raids in September 2025"
payload = {
    "query": query,
    "session_id": "test_scenario_1_live_run",
    "division": "Bengaluru Division"
}

print(f"Query: '{query}'")
print("Target Provider: zoho_quickml (Catalyst GLM 4.7 crm-di-glm47b_30b_it)")
print("Dispatching request to POST /chat...")

t0 = time.time()
res = client.post("/chat", json=payload)
t1 = time.time()

print(f"\n[HTTP Status]: {res.status_code}")
print(f"[Latency]: {(t1 - t0):.3f}s")

data = res.get_json() or {}

print(f"[Agent Type]: {data.get('agent_type')}")
print(f"[Agent Label]: {data.get('agent_label')}")
print(f"[Active Provider]: {data.get('provider')}")

charts = data.get("charts", [])
print(f"\n[Visual Charts Generated]: {len(charts)}")
for i, c in enumerate(charts, 1):
    print(f"  Chart {i}:")
    print(f"    - Title: {c.get('title')}")
    print(f"    - Type:  {c.get('type')}")
    if c.get("labels"):
        print(f"    - Labels ({len(c['labels'])}): {c.get('labels')[:5]}")
    if c.get("datasets"):
        for ds in c["datasets"]:
            print(f"    - Dataset '{ds.get('label')}': {ds.get('data')[:5]}")

print("\n[Full Executive Briefing / Narrative Response]:")
print("-" * 75)
print(data.get("answer", "No answer returned."))
print("-" * 75)

if data.get("executive_decision"):
    print("\n[Executive Decision Intelligence]:")
    print(json.dumps(data["executive_decision"], indent=2))

print("\n" + "=" * 75)
print("TEST 1 EXECUTION COMPLETE")
print("=" * 75)
