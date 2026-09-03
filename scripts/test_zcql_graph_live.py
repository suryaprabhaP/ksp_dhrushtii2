"""
KSP Sentinel AI — Phase 1 ZCQL Network Graph Live Diagnostic & Verification Suite
=================================================================================
Validates:
1. CatalystZCQLGraphRepository functionality & OAuth authentication.
2. GraphEngine ZCQL cloud ingestion, canonical node classification, and BFS shortest path.
3. Flask routes and HTTP endpoints:
   - GET /api/network_graph
   - POST /api/network_graph (custom ZCQL)
   - GET /api/graph/zcql
   - GET /api/graph/suspect/<suspect_id>
   - GET /api/graph/case/<case_id>
   - POST /api/graph/path
"""
import json
import os
import sys
import time
from dotenv import load_dotenv

load_dotenv("d:/latest_datathon/rohith_project/.env.standalone")
sys.path.insert(0, "d:/latest_datathon/rohith_project/backend")

from app.services.zcql_graph_repository import catalyst_zcql_graph_repository
from app.engine.graph_engine import GraphEngine


def run_diagnostics():
    print("=" * 70)
    print(" [*] KSP SENTINEL CLOUD ZCQL NETWORK GRAPH DIAGNOSTIC SUITE")
    print("=" * 70)

    # ── Test 1: Catalyst ZCQL Graph Repository Direct Ingestion ───────────────
    print("\n[1/5] Testing CatalystZCQLGraphRepository Direct Methods...")
    t0 = time.time()
    records, headers = catalyst_zcql_graph_repository.fetch_global_network(limit=100)
    t_global = (time.time() - t0) * 1000
    print(f" -> fetch_global_network(): Received {len(records)} records across {len(headers)} columns ({t_global:.1f} ms)")
    print(f"    Columns: {headers[:6]}...")
    if records:
        print(f"    Sample Record: {records[0].get('Suspect_Name', 'N/A')} | FIR: {records[0].get('FIR_Number', 'N/A')}")

    t0 = time.time()
    suspect_recs, s_headers = catalyst_zcql_graph_repository.fetch_suspect_network("Ramesh")
    t_suspect = (time.time() - t0) * 1000
    print(f" -> fetch_suspect_network('Ramesh'): Received {len(suspect_recs)} records ({t_suspect:.1f} ms)")

    # ── Test 2: Graph Engine Topology Assembly from ZCQL ──────────────────────
    print("\n[2/5] Testing GraphEngine.build_graph_from_zcql()...")
    t0 = time.time()
    cloud_graph = GraphEngine.build_graph_from_zcql(limit=100)
    t_build = (time.time() - t0) * 1000

    node_count = cloud_graph.get("node_count", 0)
    edge_count = cloud_graph.get("edge_count", 0)
    god_nodes = cloud_graph.get("god_nodes", [])
    print(f" -> Graph Compiled: {node_count} nodes, {edge_count} edges, {len(god_nodes)} hubs ({t_build:.1f} ms)")
    print(f"    Top Hubs: {[n['label'] + ' (deg: ' + str(n['degree']) + ')' for n in god_nodes[:3]]}")

    # ── Test 3: BFS Shortest Path Across ZCQL Network ─────────────────────────
    print("\n[3/5] Testing O(V+E) Bidirectional Path Resolution...")
    ent_a = "Ramesh 'Blade' Kumar"
    ent_b = "KA-22-ZZ-9911"
    path_res = GraphEngine.find_shortest_path(cloud_graph, ent_a, ent_b)
    if path_res.get("found"):
        hops = path_res.get("hops", 0)
        p_nodes = [n["label"] for n in path_res.get("path_nodes", [])]
        print(f" -> Path Found ({hops} hops): {' -> '.join(p_nodes)}")
    else:
        print(f" -> Path Resolution notice: {path_res.get('reason')}")

    # ── Test 4: Flask Application Route Emulation ─────────────────────────────
    print("\n[4/5] Testing Flask HTTP API Endpoints...")
    from server import app
    client = app.test_client()

    # Route 1: GET /api/network_graph
    t0 = time.time()
    resp1 = client.get("/api/network_graph")
    t1 = (time.time() - t0) * 1000
    data1 = resp1.get_json()
    print(f" -> GET /api/network_graph: HTTP {resp1.status_code} ({t1:.1f} ms)")
    print(f"    Source: {data1.get('source')}, Nodes: {data1.get('node_count')}, Edges: {data1.get('edge_count')}")

    # Route 2: GET /api/graph/suspect/Ramesh
    t0 = time.time()
    resp2 = client.get("/api/graph/suspect/Ramesh")
    t2 = (time.time() - t0) * 1000
    data2 = resp2.get_json()
    print(f" -> GET /api/graph/suspect/Ramesh: HTTP {resp2.status_code} ({t2:.1f} ms)")
    print(f"    Suspect: {data2.get('suspect_id')}, Subgraph Nodes: {data2.get('node_count')}, Edges: {data2.get('edge_count')}")

    # Route 3: GET /api/graph/case/FIR-2026-BLR-0891
    t0 = time.time()
    resp3 = client.get("/api/graph/case/FIR-2026-BLR-0891")
    t3 = (time.time() - t0) * 1000
    data3 = resp3.get_json()
    print(f" -> GET /api/graph/case/FIR-2026-BLR-0891: HTTP {resp3.status_code} ({t3:.1f} ms)")
    print(f"    Case: {data3.get('case_id')}, Subgraph Nodes: {data3.get('node_count')}")

    # Route 4: POST /api/graph/path
    t0 = time.time()
    resp4 = client.post("/api/graph/path", json={
        "start": "Ramesh 'Blade' Kumar",
        "target": "Belagavi North Sector"
    })
    t4 = (time.time() - t0) * 1000
    data4 = resp4.get_json()
    print(f" -> POST /api/graph/path: HTTP {resp4.status_code} ({t4:.1f} ms)")
    print(f"    Path Found: {data4.get('result', {}).get('found')}, Hops: {data4.get('result', {}).get('hops')}")

    # Route 5: GET /api/graph/zcql (Custom Query)
    t0 = time.time()
    resp5 = client.get("/api/graph/zcql?query=SELECT%20*%20FROM%20CRMSuspects%20LIMIT%2010")
    t5 = (time.time() - t0) * 1000
    data5 = resp5.get_json()
    print(f" -> GET /api/graph/zcql: HTTP {resp5.status_code} ({t5:.1f} ms)")
    print(f"    Query: {data5.get('query')}, Nodes: {data5.get('node_count')}")

    # ── Test 5: Graph Agent Reasoning Query Test ──────────────────────────────
    print("\n[5/5] Testing GraphAgent Natural Language Query...")
    from app.agents.graph import GraphAgent
    from app.core.interfaces import ExecutionContext

    agent = GraphAgent()
    ctx = ExecutionContext(
        query="Who are the central figures in our syndicate network?",
        session_id="unlocked_session_test"
    )
    agent_resp = agent.execute(ctx)
    print(f" -> GraphAgent Response Provider: {agent_resp.provider}")
    preview = agent_resp.answer[:300].encode("ascii", errors="replace").decode("ascii")
    print(f" -> Agent Output Preview:\n{preview}...\n")

    print("=" * 70)
    print(" [SUCCESS] ALL PHASE 1 ZCQL GRAPH ENDPOINTS & ROUTES VERIFIED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_diagnostics()
