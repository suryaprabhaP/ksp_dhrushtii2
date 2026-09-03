# Zoho Catalyst QuickML — Pipeline 4 (Crime Caseload Regression) Setup Guide

**Dataset Location:** `d:/latest_datathon/rohith_project/backend/crime_statistics_5000.csv`  
**Total Records:** 5,000 Rows  
**File Size:** ~291 KB  

---

## 1. Dataset Schema

| Column Name | Data Type | Role in QuickML | Allowed Values / Sample |
| :--- | :--- | :---: | :--- |
| **`crime_month`** | Categorical (String) | **Feature (Input)** | January, February, March, ... December |
| **`crime_year`** | Numerical (Integer) | **Feature (Input)** | 2020, 2021, 2022, 2023, 2024, 2025, 2026 |
| **`crime_category`** | Categorical (String) | **Feature (Input)** | Cyber Financial Fraud, Organized Robbery, Vehicle Theft, Narcotics Smuggling, Chain Snatching, Aggravated Assault, Illegal Arms & Ammunition, Commercial Extortion |
| **`crime_subcategory`** | Categorical (String) | **Feature (Input)** | ATM Gas Cutter Raid, Highway Heist, UPI Phishing, Crypto Extortion, Two-Wheeler Lift Gang, etc. |
| **`case_count`** | Numerical (Continuous) | 🎯 **TARGET COLUMN** | Expected incident caseload volume (e.g., 45, 120, 250, 450) |

---

## 2. Step-by-Step Pipeline Creation in Zoho Catalyst Console

1. **Navigate to QuickML:**
   - Log into **Zoho Catalyst Console** → Project `54626000000013049` (`KSPCrimeIntelligencePlatform`).
   - Go to **Discover** → **QuickML**.

2. **Upload Dataset:**
   - Click **Datasets** → **Create Dataset**.
   - Dataset Name: `KSP_CrimeStatistics_5000`.
   - Upload file: Select [`backend/crime_statistics_5000.csv`](file:///d:/latest_datathon/rohith_project/backend/crime_statistics_5000.csv).

3. **Create Training Pipeline:**
   - Click **Pipelines** → **Create Pipeline**.
   - Pipeline Name: `KSP_CrimeStatistics_Regression_Pipeline` (or use existing pipeline `3407000000006031`).
   - Problem Type: **Regression** (Predict Numerical Value).
   - Target Column: **`case_count`**.
   - Input Features: Select **`crime_month`**, **`crime_year`**, **`crime_category`**, **`crime_subcategory`**.

4. **Train & Deploy Endpoint:**
   - Run training (AutoML / Random Forest Regressor).
   - Once trained, click **Deploy Model / Endpoints**.
   - Endpoint Name: `ksp_crimestatistics_endpoint`.
   - Copy the generated:
     - **Endpoint URL** (e.g. `https://api.catalyst.zoho.in/quickml/v1/project/54626000000013049/endpoints/predict`)
     - **Endpoint Key** (`X-QUICKML-ENDPOINT-KEY`)

5. **Provide Key to Antigravity:**
   - Share the key in chat and it will be wired into `.env` to complete 100% native cloud coverage across all 4 QuickML models!
