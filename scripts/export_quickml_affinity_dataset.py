"""
Export QuickML Suspect Affinity Training Dataset (High-Volume 2500+ Records)
=============================================================================
Generates a rich, forensic-grade training dataset with 2,500+ records covering
all major crime archetypes across Karnataka districts. Tailored for QuickML
Clustering, Classification, and Similarity algorithms in Zoho Catalyst.
"""
import os
import csv
import random

def generate_quickml_affinity_dataset(output_path: str, num_records: int = 2500):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    syndicates = [
        {
            "name": "Koramangala Keyless Auto-Theft & Chop Shop Ring",
            "cluster_id": "Cluster_1_AutoTheft",
            "category": "Vehicle Theft",
            "mos": [
                "Keyless Jammer Repeater", "CAN-Bus Injector Hack", 
                "GPS Disabler OBD Override", "Chassis Number Re-Stamping",
                "Tow-Truck Impound Impersonation", "Steering Lock Acid Burn"
            ],
            "districts": ["Bengaluru Urban", "Bengaluru Rural", "Mysuru", "Belagavi", "Tumakuru", "Kolar"],
            "time_windows": ["Night (01:00 - 04:00)", "Late Night (02:00 - 05:00)", "Pre-Dawn (03:30 - 05:30)"],
            "targets": ["Luxury SUVs", "Commercial Pickup Trucks", "Sedan Fleet", "High-End Motorcycles"],
            "tools": ["Electronic Signal Amplifier", "OBD Port Programmer", "Metal Lock Pick", "RF Jammer", "Angle Grinder"]
        },
        {
            "name": "Statewide Cyber Financial Phishing & Mule Network",
            "cluster_id": "Cluster_2_CyberFraud",
            "category": "Cyber Financial Fraud",
            "mos": [
                "Electricity Bill APK Malware", "FedEx Drug Parcel Scam", 
                "Part-Time Task Telegram Trap", "SIM Swap OTP Interception",
                "Aadhaar Enabled Payment Spoofing", "Fake Loan App Extortion"
            ],
            "districts": ["Bengaluru Urban", "Hubballi-Dharwad", "Belagavi", "Mangaluru", "Kalaburagi", "Shivamogga"],
            "time_windows": ["Morning (09:00 - 12:00)", "Afternoon (13:00 - 17:00)", "Evening (17:00 - 20:00)"],
            "targets": ["Elderly Retirees", "IT Professionals", "Small Business Owners", "Housewives", "Job Seekers"],
            "tools": ["VoIP Virtual Numbers", "Mule Bank Accounts", "Remote Desktop AnyDesk APK", "Bulk SMS Gateway", "Phishing Landing Pages"]
        },
        {
            "name": "Coastal Narcotics Smuggling & Darknet Distribution",
            "cluster_id": "Cluster_3_Narcotics",
            "category": "Narcotics Smuggling",
            "mos": [
                "Fishing Boat Midnight Drop", "Interstate Vegetable Truck Concealment", 
                "Darknet Courier Postal Drop", "Student Delivery Boy Network",
                "Resort Party Dead Drop", "Chemical Lab Extraction"
            ],
            "districts": ["Mangaluru", "Udupi", "Uttara Kannada (Karwar)", "Bengaluru Urban", "Chikkamagaluru", "Kodagu"],
            "time_windows": ["Dawn (03:00 - 06:00)", "Midnight (23:00 - 02:00)", "Late Evening (21:00 - 23:30)"],
            "targets": ["College Campuses", "Nightclub Youth", "Private Resorts", "Tech Corridors"],
            "tools": ["Sealed Hydroponic Pouches", "False Floor Vehicle Cavity", "Burner SIMs", "Encrypted Signal/Session App", "Weighing Scales"]
        },
        {
            "name": "Northern Karnataka Commercial Extortion & Hawala",
            "cluster_id": "Cluster_4_Extortion",
            "category": "Commercial Extortion",
            "mos": [
                "WhatsApp VoIP Ransom Call", "Business Premise Vandalism", 
                "Stalking & Red-Ink Threat Letter", "Family Member Kidnap Threat",
                "Tender Bid Suppression Threat", "Protection Money Weekly Collection"
            ],
            "districts": ["Belagavi", "Hubballi-Dharwad", "Kalaburagi", "Ballari", "Vijayapura", "Bidar", "Raichur"],
            "time_windows": ["Evening (18:00 - 21:00)", "Night (20:00 - 23:00)", "Afternoon (14:00 - 17:00)"],
            "targets": ["Real Estate Builders", "Jewelry Shop Merchants", "Wholesale Grain Dealers", "Mining Contractors", "Petrol Bunk Owners"],
            "tools": ["Desi Country Pistol", "Unregistered Two-Wheeler", "Voice Modulator App", "Iron Rods", "Petrol Bottles"]
        },
        {
            "name": "Highway Armed Hijack & Cargo Robbery Gang",
            "cluster_id": "Cluster_5_HighwayRobbery",
            "category": "Organized Robbery",
            "mos": [
                "Spike Strip Tire Puncture", "Fake Police Barrier Stop", 
                "Rear Collision Ambush", "Driver Chemical Intoxication",
                "Overpass Rock Dropping", "Toll Booth Surveillance Follow"
            ],
            "districts": ["Tumakuru", "Kolar", "Chitradurga", "Ballari", "Davanagere", "Hassan", "Mandya"],
            "time_windows": ["Late Night (00:00 - 03:30)", "Pre-Dawn (03:30 - 05:30)", "Midnight (23:30 - 02:00)"],
            "targets": ["Cash Logistics Vans", "Highway Cargo Trailers", "Jewelry Transport Cars", "E-Commerce Delivery Trucks"],
            "tools": ["Iron Machetes", "Pepper Spray Cannister", "High-Beam Spotlight Truck", "Metal Spike Strips", "Walkie-Talkie Radios"]
        },
        {
            "name": "Gold Loan & Jewelry Burglary Syndicate",
            "cluster_id": "Cluster_6_JewelryBurglary",
            "category": "Burglary",
            "mos": [
                "Adjacent Wall Gas-Cutter Drilling", "Roof Sheet Removal Intrusion",
                "Alarm Wire Bypass & Foam Spray", "Fake Key Duplication",
                "Festival Day Empty House Target"
            ],
            "districts": ["Mysuru", "Hassan", "Mandya", "Shivamogga", "Davanagere", "Udupi", "Bengaluru Urban"],
            "time_windows": ["Midnight (01:00 - 04:00)", "Afternoon (13:00 - 15:30)", "Late Night (02:00 - 04:30)"],
            "targets": ["Gold Loan NBFCs", "Locked Gated Villas", "Traditional Jewelry Stores", "Bank Locker Branches"],
            "tools": ["Oxy-Acetylene Gas Torch", "Foam Acoustic Spray", "Diamond Glass Cutter", "Hydraulic Jack", "Signal Jammer"]
        },
        {
            "name": "Illegal Arms & Desi Weapon Trafficking Network",
            "cluster_id": "Cluster_7_ArmsTrafficking",
            "category": "Illegal Arms",
            "mos": [
                "Interstate Bus Parcel Concealment", "Agricultural Tractor Hidden Toolbox",
                "Dead-Drop Riverbed Exchange", "Customized Modification Workshop",
                "Cattle Fair Cash-and-Carry Deal"
            ],
            "districts": ["Bidar", "Yadgir", "Raichur", "Kalaburagi", "Vijayapura", "Bagalkote"],
            "time_windows": ["Dawn (04:00 - 06:30)", "Dusk (18:30 - 20:30)", "Late Night (23:00 - 01:00)"],
            "targets": ["Local Gang Operatives", "Extortion Collecters", "Illegal Sand Miners", "Factional Leaders"],
            "tools": ["Grease-Proof Waterproof Wraps", "Underground Metal Detector", "Ammunition Reloading Dies", "Modified Barrels"]
        }
    ]

    first_names = [
        "Ramesh", "Praveen", "Suresh", "Vikram", "Deepak", "Anand", "Manjunath", 
        "Imran", "Raghu", "Kiran", "Shiva", "Farhan", "Santosh", "Vijay", "Naveen",
        "Basavaraj", "Mallikarjun", "Prashanth", "Chetan", "Darshan", "Yogesh", "Girish",
        "Nadeem", "Vinay", "Sachin", "Sunil", "Ravi", "Manoj", "Ajay", "Harish", "Gopal"
    ]
    last_names = [
        "Kumar", "Shetty", "Gowda", "Patil", "Reddy", "Khan", "Hegde", "Naik", 
        "Swamy", "Pujari", "Kulkarni", "Deshmukh", "Chavan", "Bhat", "Hosamani",
        "Jadhav", "Biradar", "Inamdar", "Menon", "Acharya", "Nayaka", "Angadi"
    ]

    rows = []
    suspect_counter = 1001

    for i in range(num_records):
        synd = random.choice(syndicates)
        s_id = f"KSP-SUS-{suspect_counter}"
        suspect_counter += 1
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        # Add realistic noise/variations
        mo = random.choice(synd["mos"])
        district = random.choice(synd["districts"])
        time_window = random.choice(synd["time_windows"])
        target = random.choice(synd["targets"])
        tool = random.choice(synd["tools"])
        
        # Risk score calculation
        base_risk = 85 if synd["category"] in ["Organized Robbery", "Narcotics Smuggling", "Illegal Arms"] else 75
        risk_score = round(min(99.0, max(50.0, base_risk + random.uniform(-18.0, 14.0))), 1)
        prior_cases = random.randint(1, 15)

        rows.append({
            "suspect_id": s_id,
            "suspect_name": name,
            "primary_crime_category": synd["category"],
            "modus_operandi": mo,
            "operating_district": district,
            "time_window": time_window,
            "target_demographic": target,
            "primary_tool_or_weapon": tool,
            "prior_convictions_count": prior_cases,
            "threat_risk_score": risk_score,
            "syndicate_cluster_label": synd["cluster_id"]
        })

    fieldnames = [
        "suspect_id",
        "suspect_name",
        "primary_crime_category",
        "modus_operandi",
        "operating_district",
        "time_window",
        "target_demographic",
        "primary_tool_or_weapon",
        "prior_convictions_count",
        "threat_risk_score",
        "syndicate_cluster_label"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] Successfully generated QuickML training dataset: {output_path} ({len(rows)} records)")

if __name__ == "__main__":
    out_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "quickml_suspect_affinity_training.csv")
    generate_quickml_affinity_dataset(out_file, num_records=2500)
