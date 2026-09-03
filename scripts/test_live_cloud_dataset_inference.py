"""
KSP Sentinel AI — Live Zoho Catalyst Cloud Dataset Inference & Response Tester
==============================================================================
Loads real records from project datasets and fires live HTTPS requests to all 4
deployed Zoho Catalyst QuickML pipelines + GLM 4.7 MoE LLM.
Records and evaluates the actual JSON payloads returned by Zoho Cloud servers.
"""

import os
import sys
import json
import time
import csv
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.quickml_service import quickml_service
from app.providers.zoho_provider import ZohoQuickMLProvider


def run_live_cloud_evaluation() -> Dict[str, Any]:
    print("=" * 80)
    print("[KSP SENTINEL AI] INITIATING LIVE ZOHO CATALYST CLOUD DATASET EVALUATION")
    print("=" * 80)

    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "cloud_services_tested": [],
        "overall_summary": {
            "total_cloud_pipelines": 5,
            "cloud_success_count": 0,
            "fallback_count": 0,
            "avg_latency_ms": 0.0
        }
    }

    latencies = []

    # ──────────────────────────────────────────────────────────────────────────
    # 1. TEST PIPELINE 1: LIVE QUICKML GEOSPATIAL DBSCAN HOTSPOT CLUSTERING
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[1/5] Testing Zoho QuickML Geospatial DBSCAN Hotspot Clustering (Cloud Endpoint)...")
    # Load sample coordinate from karnataka_synthetic_crimes.csv
    csv_path = "karnataka_synthetic_crimes.csv"
    sample_coord = {"lat": 12.9716, "lon": 77.5946, "station": "Cubbon Park", "crime": "Robbery"}
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            first_row = next(reader, None)
            if first_row and "latitude" in first_row and "longitude" in first_row:
                sample_coord = {
                    "lat": float(first_row["latitude"]),
                    "lon": float(first_row["longitude"]),
                    "station": first_row.get("police_station", "Unknown PS"),
                    "crime": first_row.get("crime_type", "Extortion")
                }

    t0 = time.perf_counter()
    geo_res = quickml_service.predict_spatial_hotspot(
        latitude=sample_coord["lat"],
        longitude=sample_coord["lon"],
        severity_weight=75
    )
    t1 = time.perf_counter()
    lat_ms = (t1 - t0) * 1000
    latencies.append(lat_ms)

    geo_data = {
        "pipeline_name": "Pipeline 4: KSP Geospatial DBSCAN Hotspot Clustering",
        "cloud_model_id": "KSP_Geospatial_DBSCAN_Pipeline",
        "input_dataset_sample": sample_coord,
        "latency_ms": round(lat_ms, 2),
        "inference_source": geo_res.source,
        "status": geo_res.status,
        "returned_payload": {
            "cluster_id": geo_res.cluster_id,
            "is_hotspot": geo_res.is_hotspot,
            "confidence": geo_res.confidence,
            "explanation": geo_res.explanation
        }
    }
    results["cloud_services_tested"].append(geo_data)
    print(f"  -> Result: Cluster='{geo_res.cluster_id}', Source='{geo_res.source}', Latency={lat_ms:.2f}ms")

    # ──────────────────────────────────────────────────────────────────────────
    # 2. TEST PIPELINE 2: LIVE QUICKML SUSPECT SYNDICATE AFFINITY CLUSTERING
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[2/5] Testing Zoho QuickML Suspect Syndicate Affinity Clustering (Cloud Endpoint)...")
    affinity_sample = {
        "modus_operandi": "Gas Cutter ATM Heist",
        "district": "Bengaluru Urban",
        "crime_head": "Robbery",
        "ipc_section": "392",
        "gang_association": "D-Company_Faction_A"
    }

    t0 = time.perf_counter()
    aff_res = quickml_service.predict_suspect_affinity(affinity_sample)
    t1 = time.perf_counter()
    lat_ms = (t1 - t0) * 1000
    latencies.append(lat_ms)

    aff_data = {
        "pipeline_name": "Pipeline 1: Suspect Syndicate Affinity Clustering",
        "cloud_model_id": "CATALYST_QUICKML_AFFINITY_ENDPOINT",
        "input_dataset_sample": affinity_sample,
        "latency_ms": round(lat_ms, 2),
        "inference_source": aff_res.source,
        "status": aff_res.status,
        "returned_payload": {
            "predicted_cluster": aff_res.predicted_cluster,
            "confidence": aff_res.confidence,
            "explanation": aff_res.explanation
        }
    }
    results["cloud_services_tested"].append(aff_data)
    print(f"  -> Result: Cluster='{aff_res.predicted_cluster}', Source='{aff_res.source}', Latency={lat_ms:.2f}ms")

    # ──────────────────────────────────────────────────────────────────────────
    # 3. TEST PIPELINE 3: LIVE QUICKML TACTICAL THREAT ASSESSMENT AUTOML
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[3/5] Testing Zoho QuickML Tactical Threat Assessment AutoML (Cloud Endpoint)...")
    threat_sample = {
        "case_id": "FIR-EXT-992",
        "crime_type": "Commercial Extortion",
        "financial_loss_inr": 8500000.0,
        "police_station": "Majestic PS",
        "latitude": 12.9778,
        "longitude": 77.5728,
        "nearest_city": "Bengaluru",
        "case_status": "Under Investigation"
    }

    t0 = time.perf_counter()
    threat_res = quickml_service.predict_threat_level(threat_sample)
    t1 = time.perf_counter()
    lat_ms = (t1 - t0) * 1000
    latencies.append(lat_ms)

    threat_data = {
        "pipeline_name": "Pipeline 3: KSP Tactical Threat Assessment AutoML",
        "cloud_model_id": "KSP_Threat_AutoML_pipeline",
        "input_dataset_sample": threat_sample,
        "latency_ms": round(lat_ms, 2),
        "inference_source": threat_res.source,
        "status": threat_res.status,
        "returned_payload": {
            "threat_level": threat_res.threat_level,
            "likelihood_score": threat_res.likelihood_score,
            "explanation": threat_res.explanation
        }
    }
    results["cloud_services_tested"].append(threat_data)
    print(f"  -> Result: Threat='{threat_res.threat_level}', Likelihood={threat_res.likelihood_score}, Source='{threat_res.source}', Latency={lat_ms:.2f}ms")

    # ──────────────────────────────────────────────────────────────────────────
    # 4. TEST PIPELINE 4: LIVE QUICKML CRIME STATISTICS CASELOAD FORECASTER
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[4/5] Testing Zoho QuickML Crime Statistics Forecaster (Regression Cloud Endpoint)...")
    crime_sample = {
        "crime_year": 2026,
        "crime_month": "September",
        "crime_category": "Cyber Financial Fraud"
    }

    t0 = time.perf_counter()
    stats_res = quickml_service.predict_crime_caseload(
        crime_year=crime_sample["crime_year"],
        crime_month=crime_sample["crime_month"],
        crime_category=crime_sample["crime_category"]
    )
    t1 = time.perf_counter()
    lat_ms = (t1 - t0) * 1000
    latencies.append(lat_ms)

    stats_data = {
        "pipeline_name": "Pipeline 2: KSP Crime Statistics Forecaster (Regression)",
        "cloud_model_id": "KSP_CrimeStatistics_5000",
        "input_dataset_sample": crime_sample,
        "latency_ms": round(lat_ms, 2),
        "inference_source": stats_res.source,
        "status": stats_res.status,
        "returned_payload": {
            "predicted_case_count": stats_res.predicted_case_count,
            "confidence": stats_res.confidence,
            "explanation": stats_res.explanation
        }
    }
    results["cloud_services_tested"].append(stats_data)
    print(f"  -> Result: Predicted Cases={stats_res.predicted_case_count}, Confidence={stats_res.confidence}, Source='{stats_res.source}', Latency={lat_ms:.2f}ms")

    # ──────────────────────────────────────────────────────────────────────────
    # 5. TEST CLOUD MOE LLM: ZOHO CATALYST GLM 4.7 (crm-di-glm47b_30b_it)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[5/5] Testing Zoho Catalyst GLM 4.7 MoE LLM (Cloud LLM Endpoint)...")
    zoho_llm = ZohoQuickMLProvider()
    prompt = "Officer query: Identify high-risk extortion patterns in Majestic jurisdiction and recommend preventive measures."

    t0 = time.perf_counter()
    try:
        llm_answer, provider_used = zoho_llm.complete(
            messages=[
                {"role": "system", "content": "You are KSP Sentinel AI, a tactical police intelligence advisor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
    except Exception as e:
        llm_answer = f"Error: {e}"
        provider_used = "zoho_quickml"
    t1 = time.perf_counter()
    lat_ms = (t1 - t0) * 1000
    latencies.append(lat_ms)

    llm_success = llm_answer is not None and len(llm_answer) > 20 and not llm_answer.startswith("Error:")
    llm_data = {
        "pipeline_name": "Zoho QuickML MoE LLM Engine",
        "cloud_model_id": "crm-di-glm47b_30b_it (30B MoE)",
        "input_query": prompt,
        "latency_ms": round(lat_ms, 2),
        "cloud_inference_status": "SUCCESS_CLOUD_LLM" if llm_success else "FAIL",
        "returned_response_length": len(llm_answer or ""),
        "returned_response_snippet": (llm_answer[:250] + "...") if llm_answer else "None"
    }
    results["cloud_services_tested"].append(llm_data)
    print(f"  -> Result: Generated {len(llm_answer or '')} chars via Zoho GLM 4.7, Latency={lat_ms:.2f}ms")

    # Overall Summary
    cloud_success = sum(1 for s in results["cloud_services_tested"] if "cloud" in s.get("inference_source", "").lower() or s.get("cloud_inference_status") == "SUCCESS_CLOUD_LLM")
    results["overall_summary"]["cloud_success_count"] = cloud_success
    results["overall_summary"]["fallback_count"] = len(results["cloud_services_tested"]) - cloud_success
    results["overall_summary"]["avg_latency_ms"] = round(sum(latencies) / len(latencies), 2)

    return results


if __name__ == "__main__":
    report = run_live_cloud_evaluation()
    print("\n" + "=" * 80)
    print("[REPORT] COMPLETE CLOUD RESPONSE EVALUATION REPORT:")
    print("=" * 80)
    print(json.dumps(report, indent=2))
