import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server import app
from app.services.zoho_token_manager import zoho_token_manager
from app.services.zoho_analytics_service import zoho_analytics_service


class TestZohoAnalyticsIntegration(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_token_manager_analytics_purpose(self):
        """Verify analytics purpose is registered and resolvable in ZohoTokenManager."""
        self.assertIn("analytics", zoho_token_manager.PURPOSES)
        token = zoho_token_manager.get_valid_token(purpose="analytics")
        self.assertIsNotNone(token, "Analytics access token should not be None")
        self.assertTrue(len(token) > 10, "Analytics access token should be a valid string")

    def test_evidentiary_signature_hashing(self):
        """Verify Section 65B SHA-256 signature is deterministic and tamper-evident."""
        data1 = [{"fir": "FIR-001", "loss": 50000}]
        data2 = [{"fir": "FIR-001", "loss": 50000}]
        data3 = [{"fir": "FIR-001", "loss": 50001}]

        sig1 = zoho_analytics_service.compute_evidentiary_signature(data1)
        sig2 = zoho_analytics_service.compute_evidentiary_signature(data2)
        sig3 = zoho_analytics_service.compute_evidentiary_signature(data3)

        self.assertEqual(sig1, sig2, "Identical datasets must produce matching Section 65B hash")
        self.assertNotEqual(sig1, sig3, "Altered dataset must produce different cryptographic hash")

    def test_analytics_evidentiary_status_endpoint(self):
        """Verify GET /api/analytics/evidentiary-status returns Section 65B certification."""
        res = self.client.get("/api/analytics/evidentiary-status")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertEqual(json_data.get("status"), "CERTIFIED")
        self.assertEqual(json_data.get("cryptographic_algorithm"), "SHA-256")
        self.assertTrue(json_data.get("tamper_proof_iframe"))

    def test_analytics_dashboard_url_endpoint(self):
        """Verify GET /api/analytics/dashboard-url returns dynamic viewUrl."""
        res = self.client.get("/api/analytics/dashboard-url")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data.get("success"))
        self.assertIn("view_url", json_data)
        self.assertTrue(json_data["view_url"].startswith("https://analytics.zoho.in/"))
        self.assertTrue(json_data.get("evidentiary_certified"))


if __name__ == "__main__":
    unittest.main()
