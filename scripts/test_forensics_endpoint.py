"""
KSP Sentinel AI — End-to-End Forensics Endpoint Test
=====================================================
Tests POST /api/audio_transcribe_and_stage through Flask test client.
"""
import io
import json
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from server import app
from scripts.test_cloud_stt_live import create_synthetic_wav_bytes

def test_endpoint():
    print("=" * 70)
    print(" [*] TESTING /api/audio_transcribe_and_stage END-TO-END")
    print("=" * 70)

    client = app.test_client()
    wav_bytes = create_synthetic_wav_bytes(1.5, 440.0)

    # 1. Test Multipart Audio Upload
    data = {
        'session_id': 'forensics_test_session_001',
        'fallback_text': 'Suspect confessed to moving stolen vehicle from Majestic to Koramangala.',
        'audio': (io.BytesIO(wav_bytes), 'evidence_audio.wav', 'audio/wav')
    }

    res = client.post('/api/audio_transcribe_and_stage', data=data, content_type='multipart/form-data')
    print(f"HTTP Status: {res.status_code}")
    res_json = res.get_json() or {}
    print(f"Response Success: {res_json.get('success')}")
    print(f"Stage ID: {res_json.get('stage_id')}")
    print(f"Staged Evidence: {json.dumps(res_json.get('staged_evidence', {}), indent=2)}")

    print("\n" + "=" * 70)
    print(" [DONE] ENDPOINT VERIFICATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    test_endpoint()
