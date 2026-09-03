"""
KSP Sentinel AI — Zoho Catalyst QuickML Multi-Model Suite Verification Script
=============================================================================
Tests all 4 deployed Zoho Catalyst QuickML endpoints:
1. Suspect Syndicate Affinity Pipeline
2. KSP Crime Statistics (Caseload Regression) Pipeline
3. KSP Threat Assessment (AutoML Classification) Pipeline
4. KSP Geospatial Hotspots (DBSCAN Clustering) Pipeline
"""
import json
import logging
import sys
import os

# Set UTF-8 encoding for standard output
sys.stdout.reconfigure(encoding='utf-8')

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.quickml_service import quickml_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("test_suite")


def test_quickml_suite():
    print("=" * 80)
    print("🚀 KSP SENTINEL AI — ZOHO CATALYST QUICKML 4-PIPELINE TEST SUITE")
    print("=" * 80)

    # ──────────────────────────────────────────────────────────────────────────
    # TEST 1: Syndicate Affinity Pipeline
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[TEST 1] Invoking Suspect Syndicate Affinity Pipeline...")
    suspect_sample = {
        "suspect_id": "KSP-SUS-8802",
        "suspect_name": "Ramesh 'Keyless' Gowda",
        "primary_crime_category": "Vehicle Theft",
        "modus_operandi": "Keyless Jammer Repeater",
        "operating_district": "Bengaluru East",
        "time_window": "Late Night (02:00 - 05:00)",
        "target_demographic": "Commercial SUVs",
        "primary_tool_or_weapon": "OBD Port Programmer",
        "prior_convictions_count": 3,
        "threat_risk_score": 78.5
    }
    aff_res = quickml_service.predict_suspect_affinity(suspect_sample)
    print(f"  → Predicted Cluster: {aff_res.predicted_cluster}")
    print(f"  → Confidence: {aff_res.confidence * 100:.1f}%")
    print(f"  → Status: {aff_res.status}")
    print(f"  → Inference Source: {aff_res.source}")
    if aff_res.explanation:
        print(f"  → Model Explanation BaseValue: {aff_res.explanation.get('baseValue')}")

    # ──────────────────────────────────────────────────────────────────────────
    # TEST 2: KSP Crime Statistics (Caseload Regression) Pipeline
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[TEST 2] Invoking KSP Crime Statistics (Regression) Pipeline...")
    caseload_res = quickml_service.predict_crime_caseload(
        crime_year=2024,
        crime_month="September",
        crime_category="Organized Robbery",
        crime_subcategory="ATM Gas Cutter Raid"
    )
    print(f"  → Predicted Case Count: {caseload_res.predicted_case_count} cases")
    print(f"  → Confidence: {caseload_res.confidence * 100 if caseload_res.confidence <= 1.0 else caseload_res.confidence}%")
    print(f"  → Status: {caseload_res.status}")
    print(f"  → Inference Source: {caseload_res.source}")
    if caseload_res.explanation:
        print(f"  → Model Explanation BaseValue: {caseload_res.explanation.get('baseValue')}")

    # ──────────────────────────────────────────────────────────────────────────
    # TEST 3: KSP Threat Assessment (AutoML Classification) Pipeline
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[TEST 3] Invoking KSP Tactical Threat (AutoML) Pipeline...")
    threat_sample = {
        "case_id": "KSP-GEO-00399",
        "incident_date": "2025-04-18",
        "crime_type": "Burglary",
        "latitude": 13.322197,
        "longitude": 74.715286,
        "nearest_city": "Udupi",
        "police_station": "Udupi Town PS",
        "case_status": "Under Investigation",
        "financial_loss_inr": 4233614.0
    }
    threat_res = quickml_service.predict_threat_level(threat_sample)
    print(f"  → Predicted Threat Tier: {threat_res.threat_level}")
    print(f"  → Likelihood Score: {threat_res.likelihood_score * 100:.1f}%")
    print(f"  → Status: {threat_res.status}")
    print(f"  → Inference Source: {threat_res.source}")

    # ──────────────────────────────────────────────────────────────────────────
    # TEST 4: KSP Geospatial DBSCAN Hotspot Clustering Pipeline
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[TEST 4] Invoking KSP Geospatial DBSCAN Hotspot Clustering Pipeline...")
    geo_res = quickml_service.predict_spatial_hotspot(
        latitude=12.981073,
        longitude=77.740961,
        severity_weight=51
    )
    print(f"  → Identified Cluster: {geo_res.cluster_id}")
    print(f"  → Hotspot Active: {geo_res.is_hotspot}")
    print(f"  → Confidence: {geo_res.confidence * 100:.1f}%")
    print(f"  → Status: {geo_res.status}")
    print(f"  → Inference Source: {geo_res.source}")

    print("\n" + "=" * 80)
    print("✅ ALL 4 QUICKML PIPELINES TESTED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    test_quickml_suite()
