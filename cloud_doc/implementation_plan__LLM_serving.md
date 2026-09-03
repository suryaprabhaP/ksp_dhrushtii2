# Mixture-of-Experts (MoE) Orchestration & VLM Integration Plan

This plan outlines the integration of two complementary Mixture-of-Experts (MoE) models into the KSP Sentinel AI ecosystem, along with a complete inventory of our current active models. By intelligently routing workloads between specialized engines and cleaning up deprecated models, we achieve both high efficiency and advanced analytical capabilities.

## User Review Required
> [!IMPORTANT]
> Please review the updated model responsibilities, the complete LLM inventory (now with Gemini removed), and orchestration logic. Once you confirm this architectural design, I will proceed with code execution.

## Current LLM Ecosystem

We currently operate a resilient, multi-provider system for high availability and specialized routing. Below are the LLMs actively defined in the project (after eradicating Gemini) and their specific functions:

| Provider Class | Active Model(s) | Function / Role |
| :--- | :--- | :--- |
| **`ZohoQuickMLProvider`** | `crm-di-glm47b_30b_it` <br>(GLM-4.7-Flash) | **Primary Text Engine.** A lightweight MoE backbone. Handles primary text routing, long-context parsing, and fast agent workflows with high efficiency. |
| **`GroqProvider`** | `qwen/qwen3.8-27b`<br>`qwen/qwen3.6-27b`<br>`openai/gpt-oss-120b` | **Fast Fallback Engine.** Used as a failover for fast reasoning and strict JSON schema generation if the primary provider is busy. |
| **`ZohoQuickMLVLMProvider`**<br>*(Proposed in this plan)* | `VL-Qwen3.6-35B-A3B` | **Heavy Multimodal Engine.** A 35B parameter (3B active) MoE for complex image understanding, OCR, and deep "thinking preservation" tasks. |

## Proposed Changes

### 1. System Cleanup & Model Roles
We will eradicate legacy/redundant providers to streamline the architecture and rely on two distinct Zoho Catalyst MoE models:
*   **GLM-4.7-Flash (Lightweight Text MoE):** The high-speed, lightweight backbone. Optimized for fast reasoning, standard agent workflows, long-context tasks, and low-compute cost. This will act as our primary text router and general intelligence engine.
*   **VL-Qwen3.6-35B-A3B (Heavy Multimodal MoE):** A 35-billion-parameter (3B active, 8-bit precision) multimodal powerhouse. Designed for advanced image & text understanding, deep reasoning, agentic coding, and "thinking preservation". It will handle all visual payloads (OCR, CCTV analysis) and complex forensic reasoning.

#### [DELETE] `app/providers/gemini_provider.py`
- Completely remove the Gemini provider as we are standardizing on the Zoho Catalyst models and Groq fallback.

### 2. Multi-Model Orchestration System
#### [MODIFY] `app/providers/orchestrator.py`
We will update the `ProviderOrchestrator` to implement intent-based and payload-based routing, and eradicate Gemini references:
- **Cleanup:** Remove imports and instantiation of `GeminiProvider`.
- **Capability Tags Update:** 
  - `ZohoQuickMLProvider` (GLM-4.7-Flash) tags: `["fast_reasoning", "long_context", "agent_workflow"]`
  - `ZohoQuickMLVLMProvider` (VL-Qwen3.6-35B-A3B) tags: `["vision_enabled", "deep_reasoning", "thinking_preservation"]`
- **Routing Logic:** 
  - Standard text and context-heavy queries will default to the lightweight GLM-4.7-Flash to optimize compute.
  - A new `vlm_complete(prompt, images)` helper will strictly route image-bearing requests to VL-Qwen3.6-35B-A3B.

### 3. Agent & Software Design
#### [NEW] `app/providers/vision_base.py`
- Define `BaseVLMProvider` Interface to enforce `images: List[str]` payloads.

#### [NEW] `app/providers/zoho_vlm_provider.py`
- Implement `ZohoQuickMLVLMProvider(BaseVLMProvider)`.
- Wraps the **VL-Qwen3.6-35B-A3B** model (`/vlm/chat` endpoint).
- Prepares base64 image encoding and supports thinking preservation capabilities.

#### [MODIFY] `app/providers/zoho_provider.py`
- Ensure `ZohoQuickMLProvider` reflects the **GLM-4.7-Flash** configuration and attributes, highlighting its role as the lightweight MoE.

#### [NEW] `app/agents/vision_agent.py`
- Implement `VisionForensicsAgent`.
- Prepares dynamic system prompts for specific tasks like Crime Scene Analysis vs FIR Document OCR, feeding directly into the Qwen MoE.

### 4. API Routes
#### [NEW] `app/api/routes/vision.py`
- **Endpoint**: `POST /api/v1/vision/analyze`
- **Payload**: Accepts `multipart/form-data` with images and an optional `query`.
- **Logic**: Converts images to base64 and invokes `VisionForensicsAgent`.

#### [MODIFY] `server/main.py` (or equivalent application entry point)
- Register the new vision router with the main API application.

## Verification Plan

### Automated Tests
- Validate routing rules in `orchestrator.py`: ensure requests with `required_tags=["vision_enabled"]` are routed to the Qwen MoE, while `["fast_reasoning"]` routes to the GLM MoE. Verify that Gemini is fully disconnected.

### Manual Verification
- Execute `scripts/test_vlm_live.py` (to be created) with a sample FIR image, confirming the 35B model returns structured JSON.
- Execute `scripts/test_zoho_primary.py` to confirm the GLM-4.7-Flash engine successfully handles standard text completion at high speed.
