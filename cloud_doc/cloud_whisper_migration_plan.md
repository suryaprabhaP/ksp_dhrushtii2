# Software & System Design Plan: Cloud STT Production Migration

## Overview & Executive Summary
This document outlines the revised architectural blueprint for activating **Cloud Speech-to-Text (STT)** in **KSP Sentinel AI**. As we are migrating strictly to Zoho Cloud Production, **Zoho Zia Speech-to-Text (STT)** will act as our **Primary Engine**. 

To guarantee system resilience, **Groq Cloud Whisper (`whisper-large-v3`)** will serve as our **High-Speed Fallback Engine**. This dual-engine architecture delivers highly reliable, low-latency transcription across Kannada, Hindi, and Indian English while adhering strictly to SOLID design principles.

---

## 🏗️ System Architecture Topology

```
                         [ 🎙️ Frontend Audio Forensics ]
                           (UploadCenterView / AudioPanel)
                                        │
                                        │ POST /api/audio_transcribe_and_stage (Multipart Audio)
                                        ▼
                     [ 🛡️ Forensics HTTP Orchestrator ]
                            (app/blueprints/forensics.py)
                                        │ (Controller Layer)
                                        ▼
                 [ ⚡ Unified Cloud Audio Forensics Service ]
                          (app/services/cloud_stt_service.py)
                                        │ (Façade / Dependency Inversion)
                 ┌──────────────────────┴──────────────────────┐
                 │                                             │
                 ▼ (Primary Priority)                          ▼ (Fallback Priority)
     [ 🚀 Primary Cloud Engine ]                 [ 🛡️ Fallback Cloud Engine ]
       Zoho Zia Speech-to-Text                     Groq Whisper-large-v3
     • Native Catalyst Integration               • Sub-400ms LPU Inference
     • Enterprise Governance                     • Multilingual Audio Fallback
     • Automated OAuth Lifecycle                 
                 │                                             │
                 └──────────────────────┬──────────────────────┘
                                        │ Returns Standardized DTO: { "text": "...", "provider": "..." }
                                        ▼
                   [ ⚖️ Forensic Legal Entity Mapper ]
                     (BNS/IPC Statutory Mapping + LLM)
                                        │
                                        ▼
                     [ 💾 Session Evidence Sandbox ]
                      (DuckDB / Catalyst Data Store - Clean CRUD)
```

---

## 🛠️ Software Design & SOLID Principles

To avoid spaghetti code and hardcoding, the implementation will strictly follow these software engineering principles:

### 1. Single Responsibility Principle (SRP)
- **`ZohoSTTProvider`**: Strictly handles Zoho Catalyst API communication, OAuth token headers, and Zoho-specific error mapping.
- **`GroqSTTProvider`**: Strictly handles Groq Whisper API communication and buffering.
- **`CloudSTTService`**: Acts as the orchestrator. It manages the primary/fallback logic and normalizes the output, but does *not* know how HTTP requests are made.

### 2. Open/Closed Principle (OCP) & Dependency Inversion
- Both providers will implement a common implicit interface (or Abstract Base Class) for transcription: `transcribe(audio_bytes, filename, language) -> STTResultDTO`.
- This allows us to add a third provider (e.g., Google Cloud STT) in the future without modifying `CloudSTTService`.

### 3. No Hardcoding
- **Zero Magic Strings:** All endpoints, timeout values, retry limits, and API keys will be injected dynamically from `app.config.py` (which reads from `.env` and `app-config.json`).

### 4. Clean CRUD Operations
- Staging the transcribed evidence into DuckDB (`document_store.py`) will utilize clean CRUD operations, ensuring atomic writes and proper error handling for session persistence.

---

## 🛡️ Non-Breaking Contract Guarantee

To preserve 100% backward compatibility with all frontend UI modules (`UploadCenterView.jsx`, `AudioForensicsPanel.jsx`), the Cloud STT Service implements the exact existing contract:

```python
def transcribe_audio(
    file_bytes: bytes, 
    filename: str, 
    language: str = "en"
) -> Dict[str, Any]:
    """
    Contract Return Payload DTO:
    {
        "success": True,
        "text": "Transcribed police confession or statement narrative...",
        "language": "kn" | "en" | "hi",
        "processing_time_ms": 342,
        "provider": "zoho_zia_speech" | "cloud_whisper_large_v3"
    }
    """
```

---

## 📋 Proposed Implementation Steps

### 1. Create `app/services/cloud_stt_service.py` [NEW]
- **Primary:** Attempts transcription via `zoho_stt_service.py`.
- **Fallback:** If Zoho returns a 5xx error or times out, immediately streams the `io.BytesIO` buffer to Groq Whisper.
- **In-Memory Streaming:** Uses zero temporary disk files; pure RAM streams to protect container footprint.

### 2. Update `app/blueprints/forensics.py` [MODIFY]
- Inject `cloud_stt_service` instead of directly calling `zoho_stt_service`.
- Preserves both `/api/audio_transcribe_and_stage` and `/api/transcribe` routes with zero signature changes.

---

## 🔍 Verification Plan

### Automated Tests:
1. **Primary/Fallback Verification:**
   - Execute a synthetic test script (`scripts/test_cloud_stt_failover.py`) that forces a Zoho timeout to verify seamless handover to Groq Whisper.
2. **Contract Compliance Check:**
   - Run `backend/tests/test_phase1_contracts.py` to ensure `/api/audio_transcribe_and_stage` passes with status `200` and valid BNS legal entities.

### Manual Verification:
1. Upload a test audio file in the **Audio Forensics Panel**.
2. Verify live word-by-word streaming animation, bilingual translation, and BNS entity tagging.
