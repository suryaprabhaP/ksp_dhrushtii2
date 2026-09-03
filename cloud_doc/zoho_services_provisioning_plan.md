# Zoho Cloud & Catalyst Provisioning Plan

Based on the architectural review of the `rohith_project` codebase and the KSP Sentinel AI requirements, the following Zoho services must be provisioned, configured, and populated to ensure a production-ready, scalable deployment.

## User Review Required

> [!WARNING]
> **Production Scale & Cost Considerations**
> Deploying the full pipeline requires **Catalyst Cloud Scale** tier. Running multiple AppSail instances, QuickML inference pipelines, and real-time Event Listeners will incur compute and API usage costs. Please confirm if we should target a single-node setup for staging, or fully distributed multi-node for production.

> [!IMPORTANT]
> **Data Deletion Policy (Soft Deletes)**
> The Catalyst-to-Analytics sync CodeLib does *not* automatically replicate deleted records. We must enforce a **Soft-Delete** policy (`status = 'EXPUNGED'` or `is_deleted = true`) in the Data Store schema to ensure Analytics dashboards remain accurate. Do you approve this schema change?

## 1. Compute & Hosting (Zoho Catalyst)

*   **Catalyst AppSail (Python)**:
    *   **Purpose**: Hosts the `server.py` Flask backend.
    *   **Action**: Provision a Python AppSail container. To prevent session loss across multiple worker nodes, we will migrate the in-memory SQLite/DuckDB state to a centralized store.
*   **Catalyst Web Client**:
    *   **Purpose**: Hosts the compiled React frontend (`App.jsx`, `apiClient.js`).
    *   **Action**: Deploy the static frontend bundle.

## 2. Storage & Databases (Catalyst Data Store & File Store)

*   **Catalyst Data Store (ZCQL)**:
    *   **`crime_dataset` Table**: The primary source of truth for FIRs, entities, and spatial data. Needs to be populated with historical records. Required for the `GraphEngine`.
    *   **`officer_sessions` Table**: (New) Required to persist session states across multi-pod AppSail instances.
*   **Catalyst Cache**:
    *   **Segment: `ZohoAnalyticsDatastoreSync`**: Required by the Zoho Analytics CodeLib to manage pagination and temporary download URLs during bulk syncs.
    *   **Segment: `OAuthTokenLocks`**: (New) Distributed mutex locks for the `ZohoTokenManager` to prevent "thundering herd" OAuth refresh collisions.
*   **Catalyst File Store**:
    *   **Folder: `forensics_audio`**: Used as a staging area to spool large 15MB audio uploads to disk before sending them to Zia STT, preventing AppSail memory exhaustion.
    *   **Folder: `vision_cctv`**: Staging area for VLM image uploads.

## 3. AI & Machine Learning (QuickML & Zia)

*   **Zoho QuickML Pipelines**:
    *   We need to train and deploy 4 explicit endpoints in the Catalyst QuickML console:
        1.  `CATALYST_QUICKML_AFFINITY_ENDPOINT`: Suspect Affinity Clustering.
        2.  `CATALYST_QUICKML_CRIMESTATS_ENDPOINT`: Time-Series Crime Forecaster.
        3.  `CATALYST_QUICKML_THREAT_ENDPOINT`: Tactical Threat Assessment AutoML.
        4.  `CATALYST_QUICKML_GEOSPATIAL_ENDPOINT`: DBSCAN Hotspot Clustering.
*   **Zoho Zia Cognitive Services**:
    *   **Zia Vision/OCR**: Must be enabled in Catalyst to power the `vision.py` blueprint (FIR text extraction, CCTV face counting).
    *   **Zia Speech-to-Text (STT)**: Must be enabled for the `forensics.py` blueprint.

## 4. Business Intelligence & Event Sync

*   **Zoho Analytics Workspace**:
    *   **Purpose**: The target dashboard environment for commander-level crime statistics.
*   **Catalyst Event Listener (`ZohoAnalyticsDatastoreSyncRecord`)**:
    *   **Purpose**: Real-time mirror. Listens to `INSERT` and `UPDATE` events on the `crime_dataset` Data Store table and syncs them to Zoho Analytics.
*   **Catalyst Advanced I/O Function (`zoho_analytics_datastore_sync_routes_handler`)**:
    *   **Purpose**: Node.js/Python API component for batch historical syncs (10,000+ rows) between Data Store and Analytics.

## 5. Authentication & Identity (Zoho OAuth 2.0)

*   **Zoho API Console Application**:
    *   Register a single server-based Client Application to generate a `CLIENT_ID` and `CLIENT_SECRET`.
    *   **Required Scopes**: Scopes for Data Store, Catalyst Cache, QuickML, Zia, and Analytics.
    *   **Token Provisioning**: Generate long-lived Refresh Tokens for the `ZohoTokenManager` pools: `projects`, `tables`, `cache`, `quickml`, and `zia`.

## Verification Plan

1.  **Automated Checks**:
    *   Run `python tests/check_catalyst_connections.py` (to be created) to verify Data Store read/write, Cache segment availability, and OAuth refresh logic.
2.  **Manual Verification**:
    *   Upload a test FIR to the deployed AppSail URL and verify it propagates through the Event Listener into the Zoho Analytics workspace.
    *   Trigger a QuickML prediction via the Web Client to verify the `CATALYST_QUICKML_*` endpoints are live and respond within the 4.0s SLA.
