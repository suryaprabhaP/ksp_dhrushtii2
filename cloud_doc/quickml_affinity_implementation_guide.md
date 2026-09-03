# QuickML Affinity: Implementation Guide & Evidentiary Trust Framework

## Do We Need a Pipeline?
**Yes, absolutely.** You cannot simply point QuickML at raw database tables and expect it to instantly draw graph connections. Machine Learning requires a structured pipeline to transform raw, noisy police data into clean mathematical vectors that a model can understand, train on, and eventually run real-time inference against. 

Without a pipeline, the predictions will be slow, inaccurate, and impossible to trust.

---

## Part 1: Structural Implementation Pipeline

To implement QuickML Affinity, we must build a 4-stage pipeline:

### Stage 1: Data Extraction & Feature Engineering (The ETL Pipeline)
We must extract structured data from ZCQL and transform it into numerical features.
*   **Action:** Create a scheduled CRON job (using Catalyst Cron) to pull recent FIRs, Suspect Profiles, and existing graph edges.
*   **Feature Engineering:** Convert text and categories into numerical vectors. 
    *   *Example:* `Location: Koramangala` becomes a geospatial vector. `MO: Keyless Theft` becomes a categorical encoding. `Time: 2AM` becomes a cyclical time feature.
*   **Output:** A clean CSV or Catalyst Data Store table formatted specifically for Zoho QuickML ingestion.

### Stage 2: QuickML Model Training (The AI Pipeline)
We will use Zoho QuickML's interface to train our Affinity models.
*   **Task 1 (Clustering):** Group suspects with similar MOs and locations. (e.g., K-Means clustering).
*   **Task 2 (Similarity/Link Prediction):** Train a model to output a distance score between two suspects based on their feature vectors.
*   **Action:** Evaluate the model in the QuickML dashboard, tune hyperparameters, and deploy it to a QuickML Inference Endpoint.

### Stage 3: Backend Inference Integration (The API Pipeline)
We must connect our Python Flask backend (`GraphEngine`) to the new QuickML endpoint.
*   **Action:** Create a `QuickMLProvider` class in our backend.
*   **Workflow:** When the frontend requests an affinity graph, the backend grabs the suspect's ZCQL features, sends them to the QuickML Inference API, and receives a list of predicted associates with Confidence Scores.

### Stage 4: Graph Fusion & Delivery
Merge the deterministic data (Phase 1) with probabilistic data (Phase 2).
*   **Action:** Update the `GraphEngine` to inject these ML predictions as *Virtual Edges*.
*   **Edge Metadata:** Ensure every virtual edge contains `{"type": "prediction", "confidence": 0.85, "model_version": "v1.2"}`.

---

## Part 2: Evidentiary Trust Framework

The biggest risk of deploying AI in law enforcement is losing trust. If a model hallucinates a connection and the system presents it as fact, the system becomes a legal liability. We must implement an **Evidentiary Trust Framework**.

### 1. Strict Separation of Reality vs. Prediction
*   **Visual Distinction:** In the frontend UI, deterministic links (Shared Phone, Shared FIR) MUST be solid, thick lines. ML Predicted Links MUST be dashed, glowing, or distinctly colored (e.g., purple/orange) lines. 
*   **UI Badging:** Any suspect brought in by QuickML must have a visible badge: `"AI PREDICTION"`.

### 2. Explainability (The "Why" Factor)
A prediction is useless if we can't explain it in court. 
*   **Feature Importance:** The QuickML response must include *why* the link was drawn. 
*   **Example Tooltip:** When an officer hovers over a predicted dashed line, a tooltip must say: 
    *   *Confidence: 89%*
    *   *Reasoning: High similarity in Modus Operandi (Vehicle Theft), Operation Jurisdiction (Koramangala), and Temporal Activity (2AM - 4AM).*

### 3. Confidence Thresholds & Guardrails
*   **Minimum Viable Confidence (MVC):** The backend must aggressively filter out low-confidence guesses. Only predictions above a strict threshold (e.g., > 80% confidence) should ever reach the UI.
*   **User Controls:** Officers must have a physical toggle in the UI to turn predictions ON or OFF. The default state should be OFF (showing only hard facts).

### 4. Audit Logging
*   Every time the `QuickMLProvider` makes an inference request that results in a predicted link being displayed to an officer, we must log it in Catalyst. 
*   **Log details:** Officer ID, Timestamp, Suspect ID queried, Predicted Associate ID, Confidence Score, and Model Version. This ensures total accountability if an AI-driven lead is pursued.
