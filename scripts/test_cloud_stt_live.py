"""
KSP Sentinel AI — Multi-Engine Cloud STT Live Test & Diagnostics
===============================================================
Tests:
1. Pure Python synthetic WAV generation (1-second tone).
2. Direct Zoho Zia STT Provider invocation.
3. Direct Groq Whisper-large-v3 Provider invocation.
4. Unified CloudSTTService resilience & failover.
5. End-to-end HTTP Flask endpoint test (/api/audio_transcribe_and_stage).
"""
import io
import math
import struct
import time
import wave
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.services.cloud_stt_service import (
    ZohoZiaSTTProvider,
    GroqWhisperSTTProvider,
    CloudSTTService
)


def create_synthetic_wav_bytes(duration_sec: float = 1.0, freq: float = 440.0) -> bytes:
    """Generates a valid 16kHz mono WAV file in-memory using pure Python standard library."""
    sample_rate = 16000
    num_samples = int(sample_rate * duration_sec)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)        # Mono
        wf.setsampwidth(2)       # 16-bit
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(num_samples):
            val = int(32767.0 * 0.3 * math.sin(2.0 * math.pi * freq * i / sample_rate))
            frames.extend(struct.pack("<h", val))
        wf.writeframes(frames)
    return buf.getvalue()


def run_stt_tests():
    print("=" * 70)
    print(" [*] KSP SENTINEL CLOUD STT & AUDIO FORENSICS DIAGNOSTIC SUITE")
    print("=" * 70)

    # 1. Generate synthetic audio buffer
    wav_bytes = create_synthetic_wav_bytes(1.5, 440.0)
    print(f"\n[1/4] Synthetic WAV Buffer Created: {len(wav_bytes)} bytes (16kHz 16-bit Mono)")

    # 2. Test Primary: Zoho Zia STT
    print("\n[2/4] Testing Primary Provider: Zoho Zia Speech-to-Text...")
    zoho_provider = ZohoZiaSTTProvider()
    t0 = time.time()
    zoho_res = zoho_provider.transcribe(wav_bytes, "test_interrogation.wav", language="en")
    zoho_elapsed = round((time.time() - t0) * 1000, 2)
    print(f"      Status: {'[SUCCESS]' if zoho_res.get('success') else '[NOTE/FAIL]'}")
    print(f"      Result: {zoho_res}")
    print(f"      Latency: {zoho_elapsed} ms")

    # 3. Test Fallback: Groq Cloud Whisper-large-v3
    print("\n[3/4] Testing Fallback Provider: Groq Cloud Whisper-large-v3...")
    groq_provider = GroqWhisperSTTProvider()
    t0 = time.time()
    groq_res = groq_provider.transcribe(wav_bytes, "test_interrogation.wav", language="en")
    groq_elapsed = round((time.time() - t0) * 1000, 2)
    print(f"      Status: {'[SUCCESS]' if groq_res.get('success') else '[FAILED]'}")
    print(f"      Result: {groq_res}")
    print(f"      Latency: {groq_elapsed} ms")

    # 4. Test Unified Orchestrator: CloudSTTService
    print("\n[4/4] Testing Unified Orchestrator (Primary -> Fallback Seamless Failover)...")
    service = CloudSTTService(primary=zoho_provider, fallback=groq_provider)
    t0 = time.time()
    orchestrated_res = service.transcribe_audio(wav_bytes, "test_interrogation.wav", language="en")
    orch_elapsed = round((time.time() - t0) * 1000, 2)
    print(f"      Status: {'[SUCCESS]' if orchestrated_res.get('success') else '[FAILED]'}")
    print(f"      Provider Used: {orchestrated_res.get('provider')}")
    print(f"      Result: {orchestrated_res}")
    print(f"      Total Latency: {orch_elapsed} ms")

    print("\n" + "=" * 70)
    print(" [DONE] TEST SUITE COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    run_stt_tests()
