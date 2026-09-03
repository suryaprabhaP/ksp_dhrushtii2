"""
KSP Sentinel AI — Synthetic Dataset Generator for QuickML & Spatial Intelligence
Generates 1,000 realistic Karnataka State Police incidents with accurate coordinates,
financial losses, resolution timelines, crime categories, and risk scores.
"""
import csv
import random
from datetime import datetime, timedelta

# Karnataka Police Jurisdictions with real center coordinates
DISTRICTS = {
    "Bengaluru Urban": {
        "center": (12.9716, 77.5946),
        "stations": ["Koramangala PS", "Indiranagar PS", "Whitefield PS", "Jayanagar PS", "Cyber Crime PS Central", "Electronic City PS", "Hebbal PS", "Rajajinagar PS"]
    },
    "Mysuru": {
        "center": (12.2958, 76.6394),
        "stations": ["Lashkar PS", "Devaraja PS", "Vijayanagar Mysuru PS", "Jayalakshmipuram PS", "V.V. Puram PS", "Mandi PS"]
    },
    "Hubballi-Dharwad": {
        "center": (15.3647, 75.1240),
        "stations": ["Suburban Hubballi PS", "Town PS Dharwad", "Gokul Road PS", "Vidyanagar PS", "Old Hubballi PS"]
    },
    "Belagavi": {
        "center": (15.8497, 74.4977),
        "stations": ["Market Belagavi PS", "Camp PS", "Khade Bazar PS", "Tilakwadi PS", "APMC Belagavi PS"]
    },
    "Mangaluru": {
        "center": (12.9141, 74.8560),
        "stations": ["Kadri PS", "Bunder PS", "Urwa PS", "Panambur PS", "Kavoor PS"]
    },
    "Kalaburagi": {
        "center": (17.3297, 76.8343),
        "stations": ["Station Bazaar PS", "Chowk PS", "Brahampur PS", "Farhatabad PS", "University PS"]
    },
    "Shivamogga": {
        "center": (13.9299, 75.5681),
        "stations": ["Kote PS", "Doddapete PS", "Tunga Nagar PS", "Vinobhanagar PS"]
    },
    "Tumakuru": {
        "center": (13.3409, 77.1006),
        "stations": ["New Extension PS", "Tilak Park PS", "Kyathsandra PS", "Town PS Tumakuru"]
    }
}

CRIME_HIERARCHY = {
    "Cyber Financial Fraud": {
        "sub": ["UPI Phishing", "SIM Swap Fraud", "Investment Scam", "Crypto Extortion", "Identity Theft"],
        "loss_range": (50000, 7500000),
        "tat_range": (14, 120),
        "risk_weights": ["High", "Critical", "Medium"]
    },
    "Commercial Extortion": {
        "sub": ["Hawala Racket", "Protection Money Syndicate", "Blackmail & Ransom", "Contract Disruption"],
        "loss_range": (200000, 15000000),
        "tat_range": (30, 180),
        "risk_weights": ["Critical", "High", "High"]
    },
    "Organized Robbery": {
        "sub": ["Highway Heist", "ATM Gas Cutter Raid", "Jewellery Store Burglary", "Armed Payroll Robbery"],
        "loss_range": (150000, 5000000),
        "tat_range": (7, 90),
        "risk_weights": ["Critical", "High", "Medium"]
    },
    "Vehicle Theft": {
        "sub": ["Commercial Fleet Theft", "Two-Wheeler Lift Gang", "Luxury Car Cloning", "Chassis Tampering"],
        "loss_range": (60000, 2500000),
        "tat_range": (5, 60),
        "risk_weights": ["Medium", "Low", "High"]
    },
    "Narcotics Smuggling": {
        "sub": ["Synthetic MDMA Trafficking", "Darknet Delivery Drop", "Interstate Ganja Corridor", "Pharmaceutical Divergence"],
        "loss_range": (300000, 10000000),
        "tat_range": (20, 150),
        "risk_weights": ["Critical", "Critical", "High"]
    },
    "Chain Snatching": {
        "sub": ["Morning Walker Ambush", "Traffic Signal Grab", "Bystander Prowl"],
        "loss_range": (40000, 350000),
        "tat_range": (3, 30),
        "risk_weights": ["Medium", "High", "Low"]
    }
}

STATUSES = ["Under Investigation", "Charge Sheet Filed", "Closed", "Pending Trial", "Convicted"]

def generate_ksp_dataset(num_records=1000, output_file="d:/latest_datathon/rohith_project/backend/quickml_ksp_master_dataset.csv"):
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2026, 8, 1)
    date_delta = (end_date - start_date).days

    rows = []
    headers = [
        "case_id",
        "incident_date",
        "crime_year",
        "crime_month",
        "crime_category",
        "crime_subcategory",
        "district",
        "police_station",
        "latitude",
        "longitude",
        "financial_loss_inr",
        "case_resolution_days",
        "case_status",
        "risk_level",
        "suspect_count"
    ]

    for i in range(1, num_records + 1):
        case_id = f"KSP-FIR-{2023 + (i % 4)}-{i:05d}"
        
        # Pick random date
        random_days = random.randint(0, date_delta)
        incident_dt = start_date + timedelta(days=random_days)
        year = incident_dt.year
        month = incident_dt.month
        
        # Pick District & Station
        district_name = random.choice(list(DISTRICTS.keys()))
        district_info = DISTRICTS[district_name]
        station = random.choice(district_info["stations"])
        center_lat, center_lon = district_info["center"]
        
        # Add realistic GPS scatter around district center (~5-12 km radius)
        lat = round(center_lat + random.uniform(-0.065, 0.065), 6)
        lon = round(center_lon + random.uniform(-0.065, 0.065), 6)
        
        # Pick Crime Category & Subcategory
        crime_cat = random.choice(list(CRIME_HIERARCHY.keys()))
        cat_info = CRIME_HIERARCHY[crime_cat]
        crime_sub = random.choice(cat_info["sub"])
        
        # Financial loss & TAT
        loss = random.randint(cat_info["loss_range"][0], cat_info["loss_range"][1])
        tat = random.randint(cat_info["tat_range"][0], cat_info["tat_range"][1])
        
        # Status & Risk
        status = random.choice(STATUSES)
        risk = random.choice(cat_info["risk_weights"])
        suspects = random.randint(1, 5)
        
        rows.append([
            case_id,
            incident_dt.strftime("%Y-%m-%d"),
            year,
            month,
            crime_cat,
            crime_sub,
            district_name,
            station,
            lat,
            lon,
            loss,
            tat,
            status,
            risk,
            suspects
        ])

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"Generated {num_records} records to {output_file}")

if __name__ == "__main__":
    generate_ksp_dataset()
