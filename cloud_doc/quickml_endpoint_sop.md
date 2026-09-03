# Standard Operating Procedure (SOP): Deploying QuickML Endpoints

**Document Owner:** AI Solution Architect Team
**Target Audience:** KSP Sentinel Cloud Engineers / DevOps
**Objective:** Systematically deploy trained QuickML models as secure, accessible REST APIs (Endpoints) for the Python backend to consume, capturing the necessary API contracts.

---

## Architectural Context
Training a pipeline in Zoho QuickML creates a static model. To use this model in our live application (KSP Sentinel), we must "wrap" it in an API. QuickML Endpoints provide this wrapper. Our Flask backend will send a suspect's behavioral features (JSON) to this Endpoint URL, and the Endpoint will return the predicted Syndicate Cluster (JSON).

Since we have multiple pipelines, this SOP applies to **all of them**. You must repeat this process for each successful pipeline.

---

## Phase 1: Verification (Pre-Deployment)
Before clicking anything, verify readiness.
1. In Zoho Catalyst, navigate to **QuickML > Pipelines**.
2. Look at the `Execution Status` column. 
3. **Rule:** You can ONLY create an endpoint for a pipeline if the status is a green **`Success`**. Do not attempt this on Failed or Processing pipelines.

---

## Phase 2: Step-by-Step Endpoint Creation

Follow these precise UI interactions within the Zoho Catalyst QuickML Console.

### Step 1: Navigate to Endpoints
*   **Action:** Look at the left-hand navigation menu under the QuickML section.
*   **Click:** Click on the **`Endpoints`** tab. 

### Step 2: Initiate Creation
*   **Action:** Look in the top-right corner of the Endpoints screen.
*   **Click:** Click the prominent button labeled **`Create Endpoint`**.
*   **What you see:** A configuration modal/form will slide out or pop up.

### Step 3: Configure the Endpoint Linkage
You must now link the endpoint to the specific trained model.
*   **Field 1 (Endpoint Name):** Enter a clear, programmatic name. Do not use spaces. 
    *   *Example:* `KSP_Affinity_Predictor_API`
*   **Field 2 (Pipeline Selection):** Click the dropdown. 
    *   *Action:* Select the pipeline you just executed (e.g., `KSP_Sentinel_Behavioral_Affinity`).
*   **Field 3 (Model Selection):** Once the pipeline is selected, the Model dropdown will populate. 
    *   *Action:* Select the trained model (e.g., `KSP_Sentinel_Behavioral_Model`).

### Step 4: Security & Authentication Configuration
As a law enforcement application, security is paramount.
*   **Authentication Type:** QuickML usually offers options like *OAuth 2.0* or *AppAuthentication*.
    *   **Action:** Select the authentication method dictated by your Catalyst environment. If given a choice, choose **OAuth** or **Catalyst App Authentication** to ensure only our backend server can hit this URL.

### Step 5: Deploy
*   **Action:** At the bottom of the form, click the **`Create`** or **`Deploy`** button.
*   **Result:** QuickML will provision the serverless API. You will be redirected to the Endpoint Details page.

---

## Phase 3: Capturing the API Contract (Critical for Developers)

This is the most important step for the Solution Architecture. A deployed endpoint is useless to the backend team if we don't know the exact data structure it demands.

On the new **Endpoint Details** page, you will see a section for testing and integration. You need to extract 5 pieces of information:

### 1. Endpoint URL
*   **What to look for:** A full HTTPS URL (e.g., `https://api.catalyst.zoho.com/baas/v1/project/.../quickml/...`).
*   **Action:** Click the "Copy" icon next to it and save it.

### 2. HTTP Method
*   **What to look for:** Look for `POST`, `GET`, or `PUT`. (For ML inference, it is almost always **`POST`**).

### 3. Request Header (Authentication)
*   **What to look for:** Look at the sample code or Auth section. Find out how the token is passed.
    *   *Example:* `Authorization: Zoho-oauthtoken <TOKEN>`

### 4. The Request JSON Structure (Payload)
*   **Action:** Scroll down to the **Test Interface** section. QuickML will show you a sample JSON payload it expects based on your input features.
*   **What to look for:** It will look like a dictionary of your features.
    ```json
    {
       "modus_operandi": "string",
       "operating_district": "string",
       ...
    }
    ```
*   **Action:** Copy this exact structure. The backend team needs to know the precise spelling of these keys.

### 5. Test Execution & Response JSON Capture
You must prove the endpoint works before handing it off to the backend.
*   **Action:** In the Test Interface, enter sample dummy data for a suspect (e.g., `"modus_operandi": "Robbery"`).
*   **Click:** Click the **`Test`** or **`Predict`** button.
*   **Result:** A JSON response will appear showing the prediction.
*   **Action:** Copy the entire output JSON. We need to see exactly how QuickML formats the result (e.g., does it return `{"prediction": "Cluster_1"}` or `{"label": "Cluster_1", "confidence": 0.9}`).

---

## Next Steps for the Team
Once you have executed Phase 2 and Phase 3 for your pipeline, please reply with the **5 pieces of the API Contract** gathered in Phase 3. 

Upon receiving that contract, the backend development team (AI) will immediately begin coding `quickml_service.py` to route KSP Sentinel data to this live endpoint.
