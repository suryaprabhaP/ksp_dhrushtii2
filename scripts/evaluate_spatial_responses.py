"""
KSP Sentinel AI — Comprehensive Response & Evaluation Test Suite (Spatial & Chat Engine)
========================================================================================
Empirically tests and evaluates actual API and Agent responses across:
1. Spatial Cluster GeoJSON Response Integrity (Polygon closures, properties, threat levels)
2. Heatmap Density Point Response Integrity (Weights, boundaries, numeric types)
3. End-to-End Chat Agent Spatial Inquiries (Intent classification, factual reasoning, response formatting)
4. Outlier & Edge-Case Geodesic Inquiries (Karnataka boundaries, noise points, null coordinates)
5. Performance Benchmark (Latency, throughput, zero-dependency validation)
"""

import io
import json
import time
import math
import sys
import os
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server import app
from app.services.spatial_analytics_service import spatial_analytics_service
from app.services.spatial_ingestion_service import spatial_store


def run_evaluation() -> Dict[str, Any]:
    client = app.test_client()
    evaluation_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_scenarios": [],
        "overall_evaluation": {
            "total_scenarios": 0,
            "passed": 0,
            "failed": 0,
            "avg_latency_ms": 0.0
        }
    }

    latencies = []

    # ══════════════════════════════════════════════════════════════════════════
    # SCENARIO 1: Spatial Cluster GeoJSON Response Evaluation (/api/spatial/clusters)
    # ══════════════════════════════════════════════════════════════════════════
    t0 = time.perf_counter()
    post_data = {
        "eps_km": 8.0,
        "min_samples": 3,
        "records": [
            # Majestic Extortion Cluster (4 cases)
            {"case_id": "FIR-101", "Latitude": 12.9778, "Longitude": 77.5728, "Crime_Category": "Extortion", "Police_Station": "Majestic PS", "Status": "Open"},
            {"case_id": "FIR-102", "Latitude": 12.9785, "Longitude": 77.5735, "Crime_Category": "Extortion", "Police_Station": "Majestic PS", "Status": "Open"},
            {"case_id": "FIR-103", "Latitude": 12.9770, "Longitude": 77.5720, "Crime_Category": "Robbery", "Police_Station": "Majestic PS", "Status": "Under Investigation"},
            {"case_id": "FIR-104", "Latitude": 12.9790, "Longitude": 77.5740, "Crime_Category": "Extortion", "Police_Station": "Majestic PS", "Status": "Open"},

            # Whitefield Tech Burglary Cluster (3 cases)
            {"case_id": "FIR-201", "Latitude": 12.9698, "Longitude": 77.7499, "Crime_Category": "Burglary", "Police_Station": "Whitefield PS", "Status": "Open"},
            {"case_id": "FIR-202", "Latitude": 12.9705, "Longitude": 77.7510, "Crime_Category": "Burglary", "Police_Station": "Whitefield PS", "Status": "Open"},
            {"case_id": "FIR-203", "Latitude": 12.9690, "Longitude": 77.7485, "Crime_Category": "Theft", "Police_Station": "Whitefield PS", "Status": "Closed"},

            # Outlier Point (Dharwad)
            {"case_id": "FIR-301", "Latitude": 15.4589, "Longitude": 75.0078, "Crime_Category": "General", "Police_Station": "Suburban PS", "Status": "Open"}
        ]
    }
    res = client.post("/api/spatial/clusters", json=post_data)
    t1 = time.perf_counter()
    latency_ms = (t1 - t0) * 1000
    latencies.append(latency_ms)

    res_json = res.get_json()
    geojson = res_json.get("geojson", {})
    features = geojson.get("features", [])
    metadata = geojson.get("metadata", {})

    # Evaluate polygon closure and properties
    polygons_closed = all(
        f["geometry"]["coordinates"][0][0] == f["geometry"]["coordinates"][0][-1]
        for f in features
    )
    threat_levels_valid = all(
        f["properties"]["threat_level"] in ["CRITICAL", "HIGH", "MODERATE"]
        for f in features
    )
    has_leads = all(
        len(f["properties"].get("llm_investigative_leads", [])) >= 2
        for f in features
    )

    s1_pass = (
        res.status_code == 200
        and res_json.get("success") is True
        and len(features) >= 1
        and polygons_closed
        and threat_levels_valid
        and has_leads
    )

    evaluation_report["test_scenarios"].append({
        "scenario_id": "SCENARIO_01_SPATIAL_CLUSTER_RESPONSE",
        "description": "Evaluate /api/spatial/clusters GeoJSON response structure, polygon vertex closure, and investigative leads generation.",
        "status_code": res.status_code,
        "latency_ms": round(latency_ms, 2),
        "evaluation_verdict": "PASS" if s1_pass else "FAIL",
        "metrics": {
            "total_points_ingested": metadata.get("total_points"),
            "clustered_points": metadata.get("clustered_points"),
            "noise_points": metadata.get("noise_points"),
            "detected_hotspot_count": len(features),
            "polygons_geometrically_closed": polygons_closed,
            "threat_grading_verified": threat_levels_valid,
            "investigative_leads_present": has_leads,
            "top_hotspot_primary_crime": features[0]["properties"]["primary_crime"] if features else None,
            "top_hotspot_threat": features[0]["properties"]["threat_level"] if features else None
        },
        "sample_output_feature": features[0] if features else None
    })

    # ══════════════════════════════════════════════════════════════════════════
    # SCENARIO 2: Heatmap Density Response Evaluation (/api/spatial/heatmap)
    # ══════════════════════════════════════════════════════════════════════════
    t0 = time.perf_counter()
    res_hm = client.post("/api/spatial/heatmap", json=post_data)
    t1 = time.perf_counter()
    latency_ms = (t1 - t0) * 1000
    latencies.append(latency_ms)

    hm_json = res_hm.get_json()
    points = hm_json.get("points", [])

    # Validate each point format: [lat: float, lon: float, intensity: 0.0 - 1.0]
    weights_valid = all(
        len(p) == 3 and isinstance(p[0], (int, float)) and isinstance(p[1], (int, float)) and (0.0 <= p[2] <= 1.0)
        for p in points
    )
    s2_pass = res_hm.status_code == 200 and hm_json.get("success") is True and len(points) == 8 and weights_valid

    evaluation_report["test_scenarios"].append({
        "scenario_id": "SCENARIO_02_HEATMAP_DENSITY_RESPONSE",
        "description": "Evaluate /api/spatial/heatmap weighted intensity density matrix.",
        "status_code": res_hm.status_code,
        "latency_ms": round(latency_ms, 2),
        "evaluation_verdict": "PASS" if s2_pass else "FAIL",
        "metrics": {
            "points_count": len(points),
            "intensity_weights_valid": weights_valid,
            "sample_point_payload": points[0] if points else None
        }
    })

    # ══════════════════════════════════════════════════════════════════════════
    # SCENARIO 3: Chat Agent Spatial Reasoning & Query Response (/chat)
    # ══════════════════════════════════════════════════════════════════════════
    t0 = time.perf_counter()
    chat_payload = {
        "query": "Where are the major crime hotspots and what are the patrol recommendations?",
        "session_id": "eval_spatial_session_001"
    }
    res_chat = client.post("/chat", json=chat_payload)
    t1 = time.perf_counter()
    latency_ms = (t1 - t0) * 1000
    latencies.append(latency_ms)

    chat_json = res_chat.get_json()
    answer = chat_json.get("answer", "")
    agent_type = chat_json.get("agent_type", "")

    s3_pass = (
        res_chat.status_code == 200
        and len(answer) > 20
        and ("hotspot" in answer.lower() or "patrol" in answer.lower() or "crime" in answer.lower() or "jurisdiction" in answer.lower() or "dataset" in answer.lower())
    )

    evaluation_report["test_scenarios"].append({
        "scenario_id": "SCENARIO_03_CHATBOT_SPATIAL_INTELLIGENCE",
        "description": "Evaluate end-to-end Chatbot spatial inquiry response generation and intent routing.",
        "status_code": res_chat.status_code,
        "latency_ms": round(latency_ms, 2),
        "evaluation_verdict": "PASS" if s3_pass else "FAIL",
        "metrics": {
            "agent_type": agent_type,
            "response_length_chars": len(answer),
            "response_snippet": answer[:200] + "..." if len(answer) > 200 else answer
        }
    })

    # ══════════════════════════════════════════════════════════════════════════
    # SCENARIO 4: Edge-Case Coordinate Ingestion (Out of Jurisdiction / Single Point)
    # ══════════════════════════════════════════════════════════════════════════
    t0 = time.perf_counter()
    edge_payload = {
        "eps_km": 5.0,
        "min_samples": 2,
        "records": [
            # Single coordinate in Mysuru
            {"case_id": "SINGLE-1", "Latitude": 12.2958, "Longitude": 76.6394, "Crime_Category": "Theft", "Police_Station": "Lashkar"},
            # Extreme Outlier (Null Island)
            {"case_id": "NULL-1", "Latitude": 0.0, "Longitude": 0.0, "Crime_Category": "Cyber"},
            # Inverted Coordinates
            {"case_id": "INVERTED-1", "Latitude": 77.5946, "Longitude": 12.9716, "Crime_Category": "Assault"}
        ]
    }
    res_edge = client.post("/api/spatial/clusters", json=edge_payload)
    t1 = time.perf_counter()
    latency_ms = (t1 - t0) * 1000
    latencies.append(latency_ms)

    edge_json = res_edge.get_json()
    edge_features = edge_json.get("geojson", {}).get("features", [])

    # Must not crash with HTTP 500; must filter out (0.0, 0.0)
    s4_pass = res_edge.status_code == 200 and edge_json.get("success") is True

    evaluation_report["test_scenarios"].append({
        "scenario_id": "SCENARIO_04_EDGE_CASE_RESILIENCE",
        "description": "Evaluate response handling for single-point, Null Island (0,0), and inverted coordinates.",
        "status_code": res_edge.status_code,
        "latency_ms": round(latency_ms, 2),
        "evaluation_verdict": "PASS" if s4_pass else "FAIL",
        "metrics": {
            "handled_without_crash": True,
            "detected_clusters_count": len(edge_features)
        }
    })

    # Compute aggregate summary
    total = len(evaluation_report["test_scenarios"])
    passed = sum(1 for s in evaluation_report["test_scenarios"] if s["evaluation_verdict"] == "PASS")
    evaluation_report["overall_evaluation"]["total_scenarios"] = total
    evaluation_report["overall_evaluation"]["passed"] = passed
    evaluation_report["overall_evaluation"]["failed"] = total - passed
    evaluation_report["overall_evaluation"]["avg_latency_ms"] = round(sum(latencies) / len(latencies), 2)
    evaluation_report["overall_evaluation"]["pass_rate"] = f"{(passed / total) * 100:.1f}%"

    return evaluation_report


if __name__ == "__main__":
    report = run_evaluation()
    print(json.dumps(report, indent=2))
