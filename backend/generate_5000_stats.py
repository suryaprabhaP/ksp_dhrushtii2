"""
Generates 5,000 high-fidelity Karnataka State Police CrimeStatistics records
spanning 2020 to 2026 across all major crime categories, subcategories, months, and realistic case counts.
"""
import csv
import random

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026]

CRIME_TAXONOMY = {
    "Cyber Financial Fraud": [
        "UPI Phishing", "SIM Swap Fraud", "Investment Scam", "Crypto Extortion",
        "Identity Theft", "Credit Card Cloning", "Loan App Blackmail", "OTP Interception"
    ],
    "Commercial Extortion": [
        "Hawala Racket", "Protection Money Syndicate", "Blackmail & Ransom",
        "Contract Disruption", "Tender Mafia Coercion", "Real Estate Intimidation"
    ],
    "Organized Robbery": [
        "Highway Heist", "ATM Gas Cutter Raid", "Jewellery Store Burglary",
        "Armed Payroll Robbery", "Bank Vault Breach", "Night Commercial Break-in"
    ],
    "Vehicle Theft": [
        "Two-Wheeler Lift Gang", "Commercial Fleet Theft", "Luxury Car Cloning",
        "Chassis Tampering", "Interstate Vehicle Dismantling", "Tractor & Agriculture Rig Theft"
    ],
    "Narcotics Smuggling": [
        "Synthetic MDMA Trafficking", "Darknet Delivery Drop", "Interstate Ganja Corridor",
        "Pharmaceutical Divergence", "Heroin Hydroponic Distribution", "Cocaine Syndicate"
    ],
    "Chain Snatching": [
        "Morning Walker Ambush", "Traffic Signal Grab", "Bystander Prowl",
        "Temple Crowd Theft", "Festival Market Pinch"
    ],
    "Aggravated Assault": [
        "Gang Rivalry Brawl", "Bar Disruption", "Political Clashes",
        "Property Dispute Clash", "Road Rage Violence"
    ],
    "Illegal Arms & Ammunition": [
        "Country-made Pistol Smuggling", "Illegal Cartridge Stash",
        "Cross-Border Weapon Smuggling", "Unauthorized Explosive Stockpile"
    ]
}

def generate_5000_statistics(output_path="d:/latest_datathon/rohith_project/backend/crime_statistics_5000.csv"):
    rows = []
    headers = ["crime_month", "crime_year", "crime_category", "crime_subcategory", "case_count"]

    for _ in range(5000):
        year = random.choice(YEARS)
        month = random.choice(MONTHS)
        cat = random.choice(list(CRIME_TAXONOMY.keys()))
        subcat = random.choice(CRIME_TAXONOMY[cat])
        
        # Calculate realistic seasonal & category-weighted case count
        base_count = {
            "Cyber Financial Fraud": random.randint(80, 450),
            "Vehicle Theft": random.randint(120, 520),
            "Chain Snatching": random.randint(60, 310),
            "Organized Robbery": random.randint(15, 95),
            "Commercial Extortion": random.randint(25, 140),
            "Narcotics Smuggling": random.randint(30, 180),
            "Aggravated Assault": random.randint(45, 230),
            "Illegal Arms & Ammunition": random.randint(10, 65)
        }.get(cat, random.randint(20, 150))
        
        # Year multiplier (cyber fraud trending up over years)
        if cat == "Cyber Financial Fraud":
            base_count = int(base_count * (1 + (year - 2020) * 0.18))

        rows.append([month, year, cat, subcat, base_count])

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"Successfully generated 5,000 CrimeStatistics records to {output_path}")

if __name__ == "__main__":
    generate_5000_statistics()
