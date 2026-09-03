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

real_csv_path = "d:/latest_datathon/real_statistics_sample_dataset/8729a54d-0057-437d-8d9e-1374ef62c63f.csv"
with open(real_csv_path, "rb") as f:
    csv_bytes = f.read()

session_id = "test_real_crime_stats_session"
session_store.ingest_dataset(session_id, "ksp_violent_crimes.csv", csv_bytes)

query = "Analyze the top 5 districts with the highest Murder Rate and Causing Death by Negligence"
payload = {
    "query": query,
    "session_id": session_id,
    "division": "Karnataka State Command"
}

client = app.test_client()

print("=" * 80)
print("EXTRACTING COMPLETE CHATBOT RESPONSE FOR REAL STATISTICS DATASET")
print("=" * 80)
print(f"Query: {query}")
print(f"Session ID: {session_id}")

t0 = time.time()
res = client.post("/chat", json=payload)
t1 = time.time()

data = res.get_json() or {}

print(f"\n[HTTP Status]: {res.status_code}")
print(f"[Latency]: {(t1 - t0):.3f}s")
print(f"[Agent Type]: {data.get('agent_type')}")
print(f"[Agent Label]: {data.get('agent_label')}")
print(f"[Active Provider]: {data.get('provider')}")

print("\n" + "=" * 80)
print("FULL NARRATIVE BRIEFING:")
print("=" * 80)
print(data.get("answer", "No answer returned."))

print("\n" + "=" * 80)
print("ALL GENERATED CHARTS:")
print("=" * 80)
charts = data.get("charts", [])
print(f"Total Charts: {len(charts)}")
for i, c in enumerate(charts, 1):
    print(f"\n--- CHART {i}: {c.get('title')} ({c.get('type')}) ---")
    print(json.dumps(c, indent=2))

print("\n" + "=" * 80)
print("EXECUTIVE DECISION INTELLIGENCE:")
print("=" * 80)
print(json.dumps(data.get("executive_decision"), indent=2))

print("\n" + "=" * 80)
print("EXTRACTION COMPLETE")
print("=" * 80)
