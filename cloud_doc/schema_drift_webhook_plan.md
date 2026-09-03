# 🔄 Schema Drift Webhook & Automated Retraining Plan

## Objective
Implement an automated event-driven retraining pipeline using Webhooks so that the QuickML models adapt to new crime categorizations, police station additions, and changing jurisdictional boundaries without manual intervention.

## Current Architecture Bottleneck
- Categorical features (like `Crime Group`, `Police Station`) are one-hot encoded in QuickML during training.
- If a new type of crime emerges (e.g., "AI Drone Extortion"), QuickML inference may throw HTTP 400/500 errors for "Unseen Categorical Variable". 
- While our heuristic fallback engine safely catches these errors and provides a prediction, the machine learning models themselves become stale.

## Proposed Architecture
- Build a **Schema Drift Webhook** listener that triggers a QuickML retraining workflow whenever bulk new FIR data is uploaded.
- **Workflow Pipeline:**
  1. Officer uploads quarterly FIR CSV -> Zoho Catalyst Datastore.
  2. Data insertion triggers a Catalyst Event Function (Event Listener).
  3. The Event Function hits our Schema Drift Webhook endpoint (`/api/admin/retrain`).
  4. The webhook initiates a QuickML pipeline rerun via API, updating the model vocabulary to include new crime classes.
  5. The model is automatically deployed and the new endpoint ID is updated in the system cache.

## Implementation Steps
1. **Create the Webhook Endpoint:** Add a `/api/admin/trigger_retraining` endpoint in `server.py` protected by an admin API key.
2. **Event Integration:** Configure Zoho Catalyst Data Store events to fire a POST request to this webhook upon large batch inserts.
3. **QuickML Retraining API:** Utilize the QuickML Job API to programmatically trigger the pipeline execution for Caseload, Threat, and Hotspot models.
4. **Model Rollout:** Implement a blue-green swap logic where inference continues on the old model until the new model is successfully compiled and deployed.
