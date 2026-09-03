"""
Generates 5,000 high-precision Geospatial Crime Incident records across Karnataka
for QuickML Spatial Clustering, Hotspot Detection, and Tactical Mapping.
"""
import csv
import random
from datetime import datetime, timedelta

KARNATAKA_CITIES = {
    "Bengaluru": {
        "center": (12.9716, 77.5946),
        "stations": ["Koramangala PS", "Indiranagar PS", "Whitefield PS", "Jayanagar PS", "Cyber Crime PS Central", "Electronic City PS", "Hebbal PS", "Rajajinagar PS"]
    },
    "Mysuru": {
        "center": (12.2958, 76.6394),
        "stations": ["Lashkar PS", "Devaraja PS", "Vijayanagar Mysuru PS", "Jayalakshmipuram PS", "V.V. Puram PS", "Mandi PS"]
    },
    "Hubballi": {
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
    },
    "Ballari": {
        "center": (15.1394, 76.9214),
        "stations": ["Cowle Bazaar PS", "Brucepet PS", "Gandhi Nagar PS", "APMC Ballari PS"]
    },
    "Udupi": {
        "center": (13.3409, 74.7421),
        "stations": ["Udupi Town PS", "Malpe PS", "Manipal PS", "Padubidri PS"]
    }
}

CRIME_TYPES = [
    "Cyber Crime", "Vehicle Theft", "Robbery", "Extortion",
    "Narcotics", "Assault", "Burglary", "Chain Snatching"
]

STATUSES = ["Closed", "Under Investigation", "Charge Sheet Filed", "Open", "Convicted"]
RISK_LEVELS = ["Low", "Medium", "High", "Critical"]

def generate_5000_geospatial(output_file="d:/latest_datathon/rohith_project/backend/karnataka_crimes_5000_geospatial.csv"):
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2026, 8, 15)
    days_range = (end_date - start_date).days

    rows = []
    headers = [
        "case_id",
        "incident_date",
        "crime_type",
        "latitude",
        "longitude",
        "nearest_city",
        "police_station",
        "case_status",
        "risk_level",
        "financial_loss_inr"
    ]

    for i in range(1, 5001):
        case_id = f"KSP-GEO-{i:05d}"
        incident_dt = start_date + timedelta(days=random.randint(0, days_range))
        
        city = random.choice(list(KARNATAKA_CITIES.keys()))
        city_info = KARNATAKA_CITIES[city]
        station = random.choice(city_info["stations"])
        center_lat, center_lon = city_info["center"]
        
        # Realistic GPS scatter (Gaussian distribution clustered around city hubs)
        lat = round(random.gauss(center_lat, 0.045), 6)
        lon = round(random.gauss(center_lon, 0.045), 6)
        
        # Clamp to valid Karnataka bounding box
        lat = max(11.5, min(18.5, lat))
        lon = max(74.0, min(78.6, lon))
        
        crime_type = random.choice(CRIME_TYPES)
        status = random.choice(STATUSES)
        risk = random.choice(RISK_LEVELS)
        loss = random.randint(25000, 7500000)

        rows.append([
            case_id,
            incident_dt.strftime("%Y-%m-%d"),
            crime_type,
            lat,
            lon,
            city,
            station,
            status,
            risk,
            loss
        ])

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"Successfully generated 5,000 Geospatial Crime records to {output_file}")

if __name__ == "__main__":
    generate_5000_geospatial()
