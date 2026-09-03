import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server import app

client = app.test_client()

print("--- Testing /api/analytics/evidentiary-status ---")
res1 = client.get("/api/analytics/evidentiary-status")
print("Status:", res1.status_code)
print("Data:", res1.get_json())

print("\n--- Testing /api/analytics/dashboard-url ---")
res2 = client.get("/api/analytics/dashboard-url")
print("Status:", res2.status_code)
print("Data:", res2.get_json())

assert res1.status_code == 200, "Evidentiary status endpoint failed"
assert res2.status_code == 200, "Dashboard URL endpoint failed"
assert res2.get_json().get("success") is True, "Dashboard URL success is False"
print("\nALL FLASK ANALYTICS ENDPOINTS VERIFIED SUCCESSFULLY!")
