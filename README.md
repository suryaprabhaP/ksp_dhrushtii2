# 🛡️ KSP Sentinel AI (Drishti Command Intelligence Platform)

> **Karnataka State Police — Next-Gen AI Crime Intelligence, Multi-Agent Forensics & Command Platform**  
> *Built for Police Officers, Cyber Crime Cells, and State Intelligence Wings.*

---

## 🚀 1-Minute Quickstart (Clone & Run Locally)

Any developer or officer can clone this branch and run the entire platform locally with zero setup hassle.

### 1. Clone the Repository
```bash
git clone -b "rohith'sV0.1analysis_agent" https://github.com/suryaprabhaP/ksp_dhrushtii2.git
cd ksp_dhrushtii2
```

### 2. Start the Backend API (Flask / AppSail Engine)
```bash
# Optional: Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install lightweight dependencies (pure-Python, zero heavy C-extensions)
pip install -r requirements.txt

# Run server (default port 5000)
python server.py
```
> Backend API will be live at: `http://localhost:5000`  
> Health check: `http://localhost:5000/health`

### 3. Start the Frontend UI (React 19 + Vite)
In a separate terminal:
```bash
# Install frontend dependencies
npm install

# Launch Vite development server
npm run dev
```
> Web Client will open at: `http://localhost:5173`

---

## 🌐 Live Cloud Endpoints (Zoho Catalyst)

The system is deployed and active in production:

| Component | URL | Status |
| :--- | :--- | :--- |
| **Frontend (Web Client UI)** | [https://kspcrimeintelligenceplatform-60077159195.development.catalystserverless.in/app/index.html](https://kspcrimeintelligenceplatform-60077159195.development.catalystserverless.in/app/index.html) | **LIVE** |
| **Backend (AppSail API)** | [https://ksp-backend-50043767490.development.catalystappsail.in](https://ksp-backend-50043767490.development.catalystappsail.in) | **LIVE** |

---

## 🏛️ Key Features & Capabilities

### 1. 📊 Crime Data Analytics & Visual Intelligence Studio
* Dynamic Chart.js interactive visualizations: **Horizontal Bar Charts**, **Monthly Line Graphs**, **Proportional Doughnut Charts**, and **KPI Metric Cards**.
* **Section 65B Compliance:** Strict deterministic SQL calculations over active case records; zero number hallucination.
* **Persistent Disk Storage:** Uploaded case ledgers (`.csv`, `.xlsx`, `.json`) are stored securely per investigation session without data loss across browser reloads.

### 2. 🕸️ Network Link Intelligence
* Deterministic BFS multi-hop traversal connecting suspects, vehicles, phone numbers, and mule bank accounts.
* Syndicate kingpin hub identification and degree-of-separation analysis.

### 3. 📍 Geospatial Hotspot Radar
* Spatial DBSCAN crime density clustering across Karnataka police divisions (Bengaluru, Mysuru, Belagavi, Kalaburagi).
* Recommended police patrol routes, checkpoint (nakabandi) placements, and threat level assessments.

### 4. 🎙️ Voice Forensics & Speech Intelligence
* Kannada (`kn-IN`) and English speech-to-text transcription powered by Sarvam AI / Zoho Zia Speech.
* Audio voice readback for field briefings.

### 5. 🛡️ Citizen & Police Workflows
* **e-Complaint Portal:** Citizen incident submission with automated ticket routing.
* **Passport Verification:** Background verification and criminal ledger checks.
* **Police Spot FIR:** On-scene seizure logging and spot FIR documentation.

---

## 📂 Project Structure

```text
ksp_dhrushtii2/
├── app/                        # SOLID Modular Backend Architecture
│   ├── agents/                 # Domain Agents (analytical, document, graph, spatial, etc.)
│   ├── blueprints/             # Flask REST Blueprints (forensics, spatial, portals, vision)
│   ├── core/                   # Kernel (classifier, interfaces, registry, memory, audit)
│   ├── engine/                 # Ingestion & Compute Engines (session_store, visual_intelligence)
│   ├── providers/              # LLM Provider Abstractions (Zoho GLM/VLM, Groq, Gemini)
│   └── services/               # Catalyst Cloud Service Integrations (QuickML, ZCQL, Zia)
├── backend/                    # Catalyst AppSail Cloud Deployment Root
│   ├── app/                    # Synced cloud backend package
│   ├── server.py               # WSGI Entry point for AppSail container
│   └── app-config.json         # Catalyst AppSail configuration
├── frontend/                   # React 19 Frontend Web Client
│   ├── src/                    # Components (Chatbot, VisualStudio, Map, NetworkGraph)
│   ├── public/                 # Static assets, logos, and sample files
│   └── package.json            # Vite, React, Chart.js, Leaflet dependencies
├── scripts/                    # End-to-end verification and diagnostic test suites
├── tests/                      # Unit & integration automated test suites
├── catalyst.json               # Zoho Catalyst unified cloud deployment manifest
├── requirements.txt            # Python dependencies
├── package.json                # Root project npm scripts
├── server.py                   # Local development server entry point
└── README.md                   # Complete Quickstart & Architecture Documentation
```

---

## 📜 Legal & Forensic Evidence Compliance
All analytical operations and investigative conclusions generate an immutable Section 65B Indian Evidence Act audit record containing:
* SHA-256 content verification digest.
* Officer ID, timestamp, and query parameters.
* Model inference confidence and deterministic data source attribution.

