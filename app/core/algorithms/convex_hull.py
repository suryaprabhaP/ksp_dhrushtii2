"""
KSP Sentinel AI — Pure Python Convex Hull & Spatial Polygon Engine (SOLID Compliant)
====================================================================================
Zero C-extensions, Zero heavy dependencies (Zero shapely / numpy / scipy).
Provides O(N log N) Monotone Chain (Andrew's Algorithm) Convex Hull generation
and GeoJSON polygon buffer geometry synthesis for high-performance serverless deployment.
"""

import math
from typing import List, Tuple, Dict, Any, Optional

# Earth radius in kilometers for Haversine conversions
EARTH_RADIUS_KM = 6371.0088


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance between two GPS coordinates in kilometers.
    Pure Python implementation using math module.
    """
    if lat1 == lat2 and lon1 == lon2:
        return 0.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    # Clamp to avoid floating precision domain errors in asin
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_KM * c


def compute_convex_hull(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Computes the 2D Convex Hull for a set of points (x, y) or (lon, lat)
    using Andrew's Monotone Chain algorithm.
    Time Complexity: O(N log N)
    Returns vertices of the convex hull in counter-clockwise order.
    """
    unique_pts = sorted(list(set(points)))
    if len(unique_pts) <= 2:
        return unique_pts

    def cross_product_2d(o: Tuple[float, float], a: Tuple[float, float], b: Tuple[float, float]) -> float:
        # 2D cross product of OA and OB vectors: (a.x - o.x)*(b.y - o.y) - (a.y - o.y)*(b.x - o.x)
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    # Build lower hull
    lower: List[Tuple[float, float]] = []
    for p in unique_pts:
        while len(lower) >= 2 and cross_product_2d(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    # Build upper hull
    upper: List[Tuple[float, float]] = []
    for p in reversed(unique_pts):
        while len(upper) >= 2 and cross_product_2d(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    # Concatenate lower and upper hull (last point of each is first point of other)
    return lower[:-1] + upper[:-1]


def generate_buffered_polygon(
    points_lat_lon: List[List[float]],
    eps_km: float = 8.0,
    buffer_factor: float = 0.25,
    num_circle_segments: int = 16
) -> Dict[str, Any]:
    """
    Constructs a valid GeoJSON Polygon geometry enclosing the given lat/lon coordinates.
    Applies an adaptive geographic buffer in degrees to prevent flat/collapsed geometries.

    Input points: [[lat, lon], [lat, lon], ...]
    Output: GeoJSON geometry dict: { "type": "Polygon", "coordinates": [[[lon, lat], ...]] }
    """
    if not points_lat_lon:
        return {"type": "Polygon", "coordinates": [[]]}

    # Convert [lat, lon] to (lon, lat) as GeoJSON requires [longitude, latitude] (x, y)
    lon_lat_pts: List[Tuple[float, float]] = [(float(p[1]), float(p[0])) for p in points_lat_lon]

    # Calculate geographic buffer in degrees (1 degree lat approx 111.32 km)
    buffer_deg = max(0.004, (eps_km * buffer_factor) / 111.32)

    # 1. Single Point -> Generate circular buffer polygon
    if len(lon_lat_pts) == 1:
        cx, cy = lon_lat_pts[0]
        ring = []
        for i in range(num_circle_segments):
            angle = 2.0 * math.pi * (i / num_circle_segments)
            px = cx + buffer_deg * math.cos(angle)
            py = cy + buffer_deg * math.sin(angle)
            ring.append([round(px, 6), round(py, 6)])
        ring.append(ring[0])  # Close polygon ring
        return {"type": "Polygon", "coordinates": [ring]}

    # 2. Two Points -> Generate capsule/pill buffer polygon
    if len(lon_lat_pts) == 2:
        p1_x, p1_y = lon_lat_pts[0]
        p2_x, p2_y = lon_lat_pts[1]
        dx = p2_x - p1_x
        dy = p2_y - p1_y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return generate_buffered_polygon([[points_lat_lon[0][0], points_lat_lon[0][1]]], eps_km)

        # Unit normal vector
        nx = -dy / dist
        ny = dx / dist

        # 4 corners offset by buffer_deg
        corner1 = [round(p1_x + nx * buffer_deg - dx * 0.1, 6), round(p1_y + ny * buffer_deg - dy * 0.1, 6)]
        corner2 = [round(p2_x + nx * buffer_deg + dx * 0.1, 6), round(p2_y + ny * buffer_deg + dy * 0.1, 6)]
        corner3 = [round(p2_x - nx * buffer_deg + dx * 0.1, 6), round(p2_y - ny * buffer_deg + dy * 0.1, 6)]
        corner4 = [round(p1_x - nx * buffer_deg - dx * 0.1, 6), round(p1_y - ny * buffer_deg - dy * 0.1, 6)]
        ring = [corner1, corner2, corner3, corner4, corner1]
        return {"type": "Polygon", "coordinates": [ring]}

    # 3. Three or more points -> Compute 2D Convex Hull
    hull_vertices = compute_convex_hull(lon_lat_pts)

    if len(hull_vertices) < 3:
        # Collinear points fallback
        cx = sum(p[0] for p in lon_lat_pts) / len(lon_lat_pts)
        cy = sum(p[1] for p in lon_lat_pts) / len(lon_lat_pts)
        ring = []
        for i in range(num_circle_segments):
            angle = 2.0 * math.pi * (i / num_circle_segments)
            px = cx + (buffer_deg * 2.0) * math.cos(angle)
            py = cy + (buffer_deg * 2.0) * math.sin(angle)
            ring.append([round(px, 6), round(py, 6)])
        ring.append(ring[0])
        return {"type": "Polygon", "coordinates": [ring]}

    # Centroid of the hull
    hull_cx = sum(v[0] for v in hull_vertices) / len(hull_vertices)
    hull_cy = sum(v[1] for v in hull_vertices) / len(hull_vertices)

    # Expand hull vertices outward from centroid by buffer_deg
    buffered_ring: List[List[float]] = []
    for vx, vy in hull_vertices:
        dx = vx - hull_cx
        dy = vy - hull_cy
        length = math.hypot(dx, dy)
        if length > 0:
            scale = 1.0 + (buffer_deg / length)
            bx = hull_cx + dx * scale
            by = hull_cy + dy * scale
        else:
            bx = vx + buffer_deg
            by = vy + buffer_deg
        buffered_ring.append([round(bx, 6), round(by, 6)])

    # Close the ring
    buffered_ring.append(buffered_ring[0])

    return {
        "type": "Polygon",
        "coordinates": [buffered_ring]
    }


def pure_python_dbscan(
    coords_lat_lon: List[List[float]],
    eps_km: float = 8.0,
    min_samples: int = 4
) -> List[int]:
    """
    Pure Python Density-Based Spatial Clustering of Applications with Noise (DBSCAN).
    Calculates great-circle Haversine distances in kilometers.
    Zero C-extensions. Zero sklearn dependency.

    Parameters:
    - coords_lat_lon: List of [latitude, longitude] floats
    - eps_km: Neighborhood distance in kilometers
    - min_samples: Minimum points required to form a dense core cluster

    Returns:
    - labels: List of cluster IDs (-1 for noise, 0, 1, 2... for clusters)
    """
    n = len(coords_lat_lon)
    if n == 0:
        return []

    # Initialize all points as unvisited (label = -2)
    labels = [-2] * n
    cluster_id = 0

    # Helper: Find all neighbors within eps_km
    def get_neighbors(p_idx: int) -> List[int]:
        lat1, lon1 = coords_lat_lon[p_idx][0], coords_lat_lon[p_idx][1]
        neighbors = []
        for i in range(n):
            lat2, lon2 = coords_lat_lon[i][0], coords_lat_lon[i][1]
            if haversine_distance_km(lat1, lon1, lat2, lon2) <= eps_km:
                neighbors.append(i)
        return neighbors

    for i in range(n):
        if labels[i] != -2:
            continue

        neighbors = get_neighbors(i)
        if len(neighbors) < min_samples:
            # Mark as noise (-1) for now (can be claimed later by another cluster)
            labels[i] = -1
        else:
            # Start a new cluster
            labels[i] = cluster_id
            queue = [idx for idx in neighbors if idx != i]
            visited_in_cluster = {i}

            while queue:
                current_idx = queue.pop(0)
                if current_idx in visited_in_cluster:
                    continue
                visited_in_cluster.add(current_idx)

                if labels[current_idx] == -1:
                    # Noise point becomes border point of this cluster
                    labels[current_idx] = cluster_id

                if labels[current_idx] == -2:
                    labels[current_idx] = cluster_id
                    current_neighbors = get_neighbors(current_idx)
                    if len(current_neighbors) >= min_samples:
                        for neighbor_idx in current_neighbors:
                            if neighbor_idx not in visited_in_cluster:
                                queue.append(neighbor_idx)

            cluster_id += 1

    return labels
