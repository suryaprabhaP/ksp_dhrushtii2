import csv
import random
import math
import os

# Bengaluru and surrounding Karnataka region boundaries
LAT_MIN, LAT_MAX = 12.8, 13.1
LON_MIN, LON_MAX = 77.4, 77.8

def generate_cluster_points(center_lat, center_lon, num_points, spread):
    points = []
    for _ in range(num_points):
        # Add some random gaussian noise around the center
        lat = center_lat + random.gauss(0, spread)
        lon = center_lon + random.gauss(0, spread)
        
        # Severity weight 1 to 100. Hotspots tend to have higher severity.
        severity = min(max(int(random.gauss(60, 20)), 1), 100)
        
        points.append([round(lat, 6), round(lon, 6), severity])
    return points

def generate_noise_points(num_points):
    points = []
    for _ in range(num_points):
        lat = random.uniform(LAT_MIN - 0.2, LAT_MAX + 0.2)
        lon = random.uniform(LON_MIN - 0.2, LON_MAX + 0.2)
        severity = random.randint(1, 40)
        points.append([round(lat, 6), round(lon, 6), severity])
    return points

def main():
    print("Generating KSP Production Spatial Hotspots Dataset...")
    data = []
    
    # 1. High Density Hotspot (e.g., Majestic / City Center)
    data.extend(generate_cluster_points(12.9778, 77.5728, 1500, 0.005))
    
    # 2. Medium Density Hotspot (e.g., Koramangala)
    data.extend(generate_cluster_points(12.9279, 77.6271, 800, 0.008))
    
    # 3. Medium Density Hotspot (e.g., Whitefield / IT corridor)
    data.extend(generate_cluster_points(12.9698, 77.7499, 900, 0.010))
    
    # 4. Low Density Ring (e.g., Outer Ring Road string of incidents)
    for _ in range(300):
        angle = random.uniform(0, 2 * math.pi)
        lat = 12.95 + 0.08 * math.sin(angle) + random.gauss(0, 0.002)
        lon = 77.60 + 0.08 * math.cos(angle) + random.gauss(0, 0.002)
        severity = random.randint(30, 80)
        data.append([round(lat, 6), round(lon, 6), severity])
        
    # 5. Random Isolated Incidents (Noise - what DBSCAN filters out)
    data.extend(generate_noise_points(500))
    
    # Shuffle data to ensure random order
    random.shuffle(data)
    
    output_file = "ksp_production_spatial_hotspots.csv"
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", output_file)
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["latitude", "longitude", "severity_weight"])
        writer.writerows(data)
        
    print(f"✅ Generated {len(data)} geospatial records.")
    print(f"✅ Saved to: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    main()
