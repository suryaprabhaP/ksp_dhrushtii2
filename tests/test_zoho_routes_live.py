"""
KSP Sentinel AI — Zoho API Live Route Verification Test Suite
==============================================================
Validates all application routes that interact with Zoho Catalyst Cloud,
Zoho QuickML Pipelines, Catalyst ZCQL Data Store, and Zoho Zia Services.
"""
import json
import time
import unittest
from server import app
from app.config import KSP_ADMIN_KEY

class TestZohoProjectRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        cls.client = app.test_client()

    def test_01_audit_status_and_logs(self):
        """Validates Section 65B Audit Trail routes connected to Catalyst NoSQL Data Store."""
        t0 = time.monotonic()
        res_status = self.client.get('/api/audit/status')
        lat_status = (time.monotonic() - t0) * 1000
        
        self.assertEqual(res_status.status_code, 200)
        data_status = res_status.get_json()
        self.assertEqual(data_status.get('status'), 'active')
        self.assertEqual(data_status.get('ledger_backend'), 'Zoho Catalyst Cloud Scale NoSQL Data Store')

        t0 = time.monotonic()
        res_logs = self.client.get('/api/audit/logs?limit=5')
        lat_logs = (time.monotonic() - t0) * 1000
        self.assertEqual(res_logs.status_code, 200)
        data_logs = res_logs.get_json()
        self.assertEqual(data_logs.get('status'), 'success')
        print(f"\n[Test 1] Audit Trail: status={lat_status:.1f}ms, logs={lat_logs:.1f}ms")

    def test_02_quickml_pipeline_affinity(self):
        """Validates QuickML Pipeline 1: Suspect Syndicate Affinity Classifier."""
        payload = {
            "suspect_id": "SUSPECT-LIVE-901",
            "primary_crime_category": "Vehicle Theft",
            "modus_operandi": "GPS Jammer & OBD Flashing",
            "primary_tool_or_weapon": "OBD Programmer",
            "target_demographic": "Automobile Owners"
        }
        t0 = time.monotonic()
        res = self.client.post('/api/quickml/predict_affinity', json=payload)
        lat = (time.monotonic() - t0) * 1000
        
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('predicted_cluster', data)
        print(f"\n[Test 2] QuickML Affinity: latency={lat:.1f}ms, cluster={data.get('predicted_cluster')}, status={data.get('status')}")

    def test_03_quickml_pipeline_caseload(self):
        """Validates QuickML Pipeline 2: KSP Crime Statistics Caseload Forecaster."""
        payload = {
            "crime_year": 2026,
            "crime_month": "October",
            "crime_category": "Vehicle Theft",
            "crime_subcategory": "Automobile Heist"
        }
        t0 = time.monotonic()
        res = self.client.post('/api/quickml/predict_caseload', json=payload)
        lat = (time.monotonic() - t0) * 1000
        
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('predicted_case_count', data)
        print(f"\n[Test 3] QuickML Caseload: latency={lat:.1f}ms, count={data.get('predicted_case_count')}, status={data.get('status')}")

    def test_04_quickml_pipeline_threat(self):
        """Validates QuickML Pipeline 3: Tactical Threat Assessment Classifier."""
        payload = {
            "threat_factors": {
                "violence_history": 8,
                "firearm_involvement": 1,
                "syndicate_ties": 9,
                "evasion_risk": 7
            }
        }
        t0 = time.monotonic()
        res = self.client.post('/api/quickml/predict_threat', json=payload)
        lat = (time.monotonic() - t0) * 1000
        
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('threat_level', data)
        print(f"\n[Test 4] QuickML Threat: latency={lat:.1f}ms, level={data.get('threat_level')}, status={data.get('status')}")

    def test_05_quickml_pipeline_hotspot(self):
        """Validates QuickML Pipeline 4: Geospatial DBSCAN Hotspot Clustering."""
        payload = {
            "latitude": 12.9716,
            "longitude": 77.5946,
            "incident_type": "Robbery",
            "time_window_days": 30
        }
        t0 = time.monotonic()
        res = self.client.post('/api/quickml/predict_hotspot', json=payload)
        lat = (time.monotonic() - t0) * 1000
        
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('cluster_id', data)
        print(f"\n[Test 5] QuickML Hotspot: latency={lat:.1f}ms, cluster={data.get('cluster_id')}, status={data.get('status')}")

    def test_06_admin_trigger_retraining(self):
        """Validates QuickML Cloud Pipeline Retraining Dispatch Endpoint."""
        payload = {
            "pipeline_type": "crimestats"
        }
        headers = {
            "Authorization": f"Bearer {KSP_ADMIN_KEY}"
        }
        t0 = time.monotonic()
        res = self.client.post('/api/admin/trigger_retraining', json=payload, headers=headers)
        lat = (time.monotonic() - t0) * 1000
        
        self.assertEqual(res.status_code, 202)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        print(f"\n[Test 6] QuickML Retraining Webhook: latency={lat:.1f}ms, msg={data.get('message')}")

    def test_07_graph_zcql_and_nexus(self):
        """Validates Catalyst ZCQL Graph Intelligence & BFS Nexus Shortest-Path."""
        # 1. ZCQL query
        t0 = time.monotonic()
        res_zcql = self.client.post('/api/graph/zcql', json={"query": "SELECT * FROM PoliceFIRs", "limit": 20})
        lat_zcql = (time.monotonic() - t0) * 1000
        self.assertEqual(res_zcql.status_code, 200)
        data_zcql = res_zcql.get_json()
        self.assertIn('nodes', data_zcql)

        # 2. Path resolution
        t0 = time.monotonic()
        res_path = self.client.post('/api/graph/path', json={"start": "SUSPECT-01", "target": "SUSPECT-02"})
        lat_path = (time.monotonic() - t0) * 1000
        self.assertEqual(res_path.status_code, 200)
        data_path = res_path.get_json()
        self.assertTrue(data_path.get('success'))
        print(f"\n[Test 7] Catalyst ZCQL & Graph Nexus: zcql={lat_zcql:.1f}ms, path={lat_path:.1f}ms")

    def test_08_chat_federated_agent(self):
        """Validates POST /chat invoking Federated & Sub-Agents with Zoho QuickML LLM routing."""
        payload = {
            "query": "Give me an executive summary of the vehicle theft network in Bengaluru",
            "session_id": "test_zoho_route_session"
        }
        t0 = time.monotonic()
        res = self.client.post('/chat', json=payload)
        lat = (time.monotonic() - t0) * 1000
        
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('answer', data)
        self.assertIn('agent_type', data)
        print(f"\n[Test 8] POST /chat (Live Federated Agent): latency={lat:.1f}ms, agent={data.get('agent_type')}")

    def test_09_zoho_tts_synthesis(self):
        """Validates Zoho Zia Text-to-Speech synthesis route."""
        payload = {
            "text": "Alert: High priority suspect tracked near MG Road.",
            "language": "en"
        }
        t0 = time.monotonic()
        res = self.client.post('/api/zoho_tts', json=payload)
        lat = (time.monotonic() - t0) * 1000
        
        data = res.get_json()
        print(f"\n[Test 9] Zia TTS Route: latency={lat:.1f}ms, success={data.get('success')}")
        self.assertIn('success', data)

if __name__ == '__main__':
    unittest.main()
