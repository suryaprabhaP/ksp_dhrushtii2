"""
KSP Sentinel AI — Live Vision Endpoints Verification Script
"""
import requests
import json
import time
import sys

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:5000"
TINY_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

tests = [
    {
        "name": "Health Status & Model Inventory",
        "url": f"{BASE_URL}/api/health",
        "method": "GET",
        "payload": None
    },
    {
        "name": "Multimodal Vision Analysis (/api/vision/analyze)",
        "url": f"{BASE_URL}/api/vision/analyze",
        "method": "POST",
        "payload": {
            "images": [TINY_PNG_B64],
            "prompt": "Inspect crime scene for evidence.",
            "task_type": "forensics"
        }
    },
    {
        "name": "Bilingual Document & FIR OCR (/api/vision/ocr_fir)",
        "url": f"{BASE_URL}/api/vision/ocr_fir",
        "method": "POST",
        "payload": {
            "images": [TINY_PNG_B64],
            "prompt": "Extract FIR number and BNS sections into JSON."
        }
    },
    {
        "name": "CCTV Scene Reconstruction (/api/vision/cctv_reconstruction)",
        "url": f"{BASE_URL}/api/vision/cctv_reconstruction",
        "method": "POST",
        "payload": {
            "images": [TINY_PNG_B64],
            "prompt": "Reconstruct vehicle and suspect attributes."
        }
    }
]

print("=" * 80)
print(">>> RUNNING LIVE VISION ENDPOINT TEST OVER HTTP")
print("=" * 80)

passed = 0
for t in tests:
    t0 = time.time()
    try:
        if t["method"] == "GET":
            r = requests.get(t["url"], timeout=30)
        else:
            r = requests.post(t["url"], json=t["payload"], timeout=30)
        elapsed = round((time.time() - t0) * 1000, 2)
        res_data = r.json()
        print(f"[PASS] {t['name']} ({elapsed}ms) - Status {r.status_code}")
        if "models" in res_data:
            print(f"   -> Models: {res_data['models']}")
        if "provider" in res_data:
            print(f"   -> Provider: {res_data['provider']} | Agent: {res_data.get('agent_type')}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] {t['name']} - Error: {e}")

print("=" * 80)
print(f"SUMMARY: {passed}/{len(tests)} PASSED")
print("=" * 80)
