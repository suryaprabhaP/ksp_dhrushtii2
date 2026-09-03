"""
KSP Sentinel AI — Cloud Text-to-Speech (TTS) Live Diagnostic & Verification
===========================================================================
Tests:
1. Direct Zoho Zia Text-to-Audio Synthesis Provider (English, Hindi, Kannada).
2. End-to-end HTTP Flask endpoints (/api/sarvam_tts, /api/cloud_tts, /api/zoho_tts).
3. Payload format, Base64 validation, audio info inspection.
"""
import base64
import json
import sys
import time
from pathlib import Path

# Add paths
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.services.cloud_tts_service import ZohoZiaTTSProvider, cloud_tts_service
from server import app


def test_direct_zoho_tts():
    print("=" * 70)
    print(" [*] TESTING ZOHO ZIA TEXT-TO-SPEECH (TTS) DIRECT PROVIDER")
    print("=" * 70)

    provider = ZohoZiaTTSProvider()

    test_cases = [
        {
            "lang": "en",
            "speaker": "Mary",
            "text": "Karnataka State Police Sentinel AI is active and monitoring district operations."
        },
        {
            "lang": "hi",
            "speaker": "Divya",
            "text": "\u092d\u093e\u0930\u0924 \u090f\u0915 \u092e\u0939\u093e\u0928 \u0926\u0947\u0936 \u0939\u0948\u0964"
        },
        {
            "lang": "kn",
            "speaker": "Anu",
            "text": "\u0c95\u0cb0\u0ccd\u0ca8\u0cbe\u0c9f\u0c95 \u0cb0\u0cbe\u0c9c\u0ccd\u0caf \u0caa\u0cca\u0cb2\u0cc0\u0cb8\u0ccd \u0cb5\u0ccd\u0caf\u0cb5\u0cb8\u0ccd\u0ca5\u0cc6 \u0cb8\u0c95\u0ccd\u0cb0\u0cbf\u0caf\u0cb5\u0cbe\u0c97\u0cbf\u0ca6\u0cc6."
        }
    ]

    for tc in test_cases:
        print(f"\n--- Synthesizing [{tc['lang'].upper()}] (Speaker: {tc['speaker']}) ---")
        t0 = time.time()
        res = provider.synthesize(
            text=tc["text"],
            language=tc["lang"],
            speaker=tc["speaker"]
        )
        elapsed = round((time.time() - t0) * 1000, 2)
        success = res.get("success", False)
        print(f"Status: {'[SUCCESS]' if success else '[FAILED]'}")
        print(f"Provider: {res.get('provider')}")
        print(f"Latency: {elapsed} ms (Internal Processing: {res.get('processing_time_ms')} ms)")
        if success:
            audio_bytes = res.get("audio_bytes", b"")
            print(f"WAV Audio Bytes: {len(audio_bytes)} bytes")
            print(f"Base64 String Length: {len(res.get('audio_b64', ''))} chars")
            print(f"Audio Info: {json.dumps(res.get('audio_info', {}), indent=2)}")
        else:
            print(f"Error: {res.get('error')}")


def test_flask_endpoints():
    print("\n" + "=" * 70)
    print(" [*] TESTING FLASK HTTP TTS ENDPOINTS")
    print("=" * 70)

    client = app.test_client()

    endpoints = ["/api/sarvam_tts", "/api/cloud_tts", "/api/zoho_tts"]
    for ep in endpoints:
        print(f"\n--- Testing Endpoint: POST {ep} ---")
        payload = {
            "text": "Attention officer. High risk financial fraud pattern detected in Bengaluru East.",
            "language_code": "en-IN"
        }
        res = client.post(ep, json=payload)
        print(f"HTTP Status: {res.status_code}")
        res_json = res.get_json() or {}
        print(f"Response Success: {res_json.get('success')}")
        print(f"Provider: {res_json.get('provider')}")
        print(f"Language: {res_json.get('language')}")
        print(f"Speaker: {res_json.get('speaker')}")
        print(f"Processing Time: {res_json.get('processing_time_ms')} ms")
        print(f"Audio B64 Sample: {str(res_json.get('audio_b64', ''))[:30]}...")

    print("\n" + "=" * 70)
    print(" [DONE] TTS DIAGNOSTIC SUITE COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    test_direct_zoho_tts()
    test_flask_endpoints()
