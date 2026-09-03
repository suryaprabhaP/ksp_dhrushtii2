"""
KSP Sentinel AI — Pure Python Spatial & DBSCAN Migration Verification Test Suite
================================================================================
Empirical unit & integration tests verifying:
1. Pure Python Convex Hull (Andrew's Monotone Chain) & GeoJSON Polygon generation
2. Haversine distance accuracy
3. Zero-dependency Pure Python DBSCAN clustering & noise isolation
4. SpatialAnalyticsService GeoJSON FeatureCollection assembly & threat scoring
5. Heatmap payload generation
6. Flask REST endpoints (/api/spatial/clusters, /api/spatial/heatmap)
7. Zero heavy C-dependency verification (runs without sklearn/shapely/numpy)
"""

import math
import unittest
from typing import List, Dict, Any

from app.core.algorithms.convex_hull import (
    haversine_distance_km,
    compute_convex_hull,
    generate_buffered_polygon,
    pure_python_dbscan
)
from app.services.spatial_analytics_service import spatial_analytics_service


class TestPurePythonConvexHullAndGeometry(unittest.TestCase):
    """Test mathematical accuracy of the pure Python geometry engine."""

    def test_haversine_distance_bangalore_to_mysuru(self):
        # Bangalore (Majestic): 12.9778° N, 77.5728° E
        # Mysuru (Palace): 12.3052° N, 76.6552° E
        dist = haversine_distance_km(12.9778, 77.5728, 12.3052, 76.6552)
        # Expected great circle distance is approx 125 - 135 km
        self.assertTrue(120.0 <= dist <= 140.0, f"Distance {dist} km out of expected range 120-140 km")

    def test_haversine_distance_zero(self):
        dist = haversine_distance_km(12.97, 77.59, 12.97, 77.59)
        self.assertEqual(dist, 0.0)

    def test_compute_convex_hull_square(self):
        points = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.5, 0.5)]
        hull = compute_convex_hull(points)
        self.assertEqual(len(hull), 4)
        self.assertNotIn((0.5, 0.5), hull)

    def test_compute_convex_hull_collinear(self):
        points = [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]
        hull = compute_convex_hull(points)
        self.assertTrue(len(hull) >= 2)

    def test_generate_buffered_polygon_single_point(self):
        geojson = generate_buffered_polygon([[12.97, 77.59]], eps_km=8.0)
        self.assertEqual(geojson["type"], "Polygon")
        self.assertEqual(len(geojson["coordinates"]), 1)
        coords = geojson["coordinates"][0]
        self.assertTrue(len(coords) >= 16)
        # Ring must be closed
        self.assertEqual(coords[0], coords[-1])

    def test_generate_buffered_polygon_multi_points(self):
        pts = [
            [12.9778, 77.5728],
            [12.9810, 77.5790],
            [12.9720, 77.5810],
            [12.9750, 77.5690]
        ]
        geojson = generate_buffered_polygon(pts, eps_km=5.0)
        self.assertEqual(geojson["type"], "Polygon")
        coords = geojson["coordinates"][0]
        self.assertTrue(len(coords) >= 4)
        self.assertEqual(coords[0], coords[-1])


class TestPurePythonDBSCAN(unittest.TestCase):
    """Test clustering fidelity and noise handling without scikit-learn."""

    def test_two_distinct_clusters_and_noise(self):
        # Cluster 1: Bangalore Majestic area (~12.97° N, 77.57° E)
        c1 = [
            [12.9778, 77.5728],
            [12.9780, 77.5730],
            [12.9775, 77.5725],
            [12.9782, 77.5732],
            [12.9779, 77.5729]
        ]
        # Cluster 2: Koramangala area (~12.93° N, 77.62° E, approx 7-8 km away)
        c2 = [
            [12.9352, 77.6245],
            [12.9355, 77.6248],
            [12.9350, 77.6242],
            [12.9358, 77.6250]
        ]
        # Noise point: Isolated coordinate in Hassan / Tumakuru (80 km away)
        noise = [
            [13.3400, 77.1000]
        ]

        all_coords = c1 + c2 + noise
        labels = pure_python_dbscan(all_coords, eps_km=2.0, min_samples=3)

        self.assertEqual(len(labels), len(all_coords))

        # C1 points should all share the same cluster ID
        c1_labels = labels[:5]
        self.assertEqual(len(set(c1_labels)), 1)
        self.assertNotEqual(c1_labels[0], -1)

        # C2 points should all share the same cluster ID, distinct from C1
        c2_labels = labels[5:9]
        self.assertEqual(len(set(c2_labels)), 1)
        self.assertNotEqual(c2_labels[0], -1)
        self.assertNotEqual(c1_labels[0], c2_labels[0])

        # Noise point must be labeled as -1
        self.assertEqual(labels[9], -1)


class TestSpatialAnalyticsServiceIntegration(unittest.TestCase):
    """Test end-to-end service orchestration, GeoJSON formatting, and threat level assignment."""

    def setUp(self):
        self.synthetic_crimes = [
            # Hotspot 1: High severity armed extortion in Central
            {"case_id": "FIR-001", "Latitude": 12.9778, "Longitude": 77.5728, "Crime_Category": "Extortion", "Police_Station": "Majestic PS", "Status": "Under Investigation"},
            {"case_id": "FIR-002", "Latitude": 12.9780, "Longitude": 77.5730, "Crime_Category": "Extortion", "Police_Station": "Majestic PS", "Status": "Open"},
            {"case_id": "FIR-003", "Latitude": 12.9775, "Longitude": 77.5725, "Crime_Category": "Extortion", "Police_Station": "Majestic PS", "Status": "Charge Sheeted"},
            {"case_id": "FIR-004", "Latitude": 12.9782, "Longitude": 77.5732, "Crime_Category": "Robbery", "Police_Station": "Majestic PS", "Status": "Open"},
            {"case_id": "FIR-005", "Latitude": 12.9779, "Longitude": 77.5729, "Crime_Category": "Extortion", "Police_Station": "Majestic PS", "Status": "Under Investigation"},

            # Hotspot 2: Cyber theft in Tech Corridor
            {"case_id": "FIR-006", "Latitude": 12.9352, "Longitude": 77.6245, "Crime_Category": "Theft", "Police_Station": "Koramangala PS", "Status": "Open"},
            {"case_id": "FIR-007", "Latitude": 12.9355, "Longitude": 77.6248, "Crime_Category": "Theft", "Police_Station": "Koramangala PS", "Status": "Open"},
            {"case_id": "FIR-008", "Latitude": 12.9350, "Longitude": 77.6242, "Crime_Category": "Theft", "Police_Station": "Koramangala PS", "Status": "Closed"},
            {"case_id": "FIR-009", "Latitude": 12.9358, "Longitude": 77.6250, "Crime_Category": "Theft", "Police_Station": "Koramangala PS", "Status": "Open"},

            # Outlier / Noise Point
            {"case_id": "FIR-010", "Latitude": 13.8000, "Longitude": 75.0000, "Crime_Category": "General", "Police_Station": "Remote PS", "Status": "Open"}
        ]

    def test_detect_hotspots_dbscan_geojson_output(self):
        geojson = spatial_analytics_service.detect_hotspots_dbscan(
            records=self.synthetic_crimes,
            eps_km=3.0,
            min_samples=3
        )

        self.assertEqual(geojson["type"], "FeatureCollection")
        self.assertIn("features", geojson)
        self.assertIn("metadata", geojson)

        features = geojson["features"]
        self.assertEqual(len(features), 2, "Expected exactly 2 distinct clusters detected")

        # Verify Feature #1 (Majestic PS Extortion)
        f1 = features[0]
        self.assertEqual(f1["type"], "Feature")
        self.assertEqual(f1["geometry"]["type"], "Polygon")
        self.assertEqual(f1["properties"]["rank"], 1)
        self.assertEqual(f1["properties"]["incident_count"], 5)
        self.assertEqual(f1["properties"]["primary_crime"], "Extortion")
        self.assertEqual(f1["properties"]["top_station"], "Majestic PS")
        self.assertIn("centroid", f1["properties"])
        self.assertEqual(len(f1["properties"]["centroid"]), 2)

        # Verify metadata summary
        meta = geojson["metadata"]
        self.assertEqual(meta["total_points"], 10)
        self.assertEqual(meta["clustered_points"], 9)
        self.assertEqual(meta["noise_points"], 1)
        self.assertEqual(meta["cluster_count"], 2)

    def test_heatmap_payload_generation(self):
        payload = spatial_analytics_service.generate_heatmap_payload(self.synthetic_crimes)
        self.assertTrue(payload["success"])
        self.assertEqual(payload["count"], 10)
        points = payload["points"]
        self.assertEqual(len(points), 10)
        # Each point must be [lat, lon, weight]
        for pt in points:
            self.assertEqual(len(pt), 3)
            self.assertTrue(0.0 <= pt[2] <= 1.0)


class TestFlaskBlueprintEndpoints(unittest.TestCase):
    """Test Flask HTTP routes for spatial endpoints."""

    @classmethod
    def setUpClass(cls):
        from server import app
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_spatial_clusters_endpoint(self):
        post_payload = {
            "eps_km": 4.0,
            "min_samples": 2,
            "records": [
                {"case_id": "C-1", "Latitude": 12.9778, "Longitude": 77.5728, "Crime_Category": "Theft"},
                {"case_id": "C-2", "Latitude": 12.9780, "Longitude": 77.5730, "Crime_Category": "Theft"},
                {"case_id": "C-3", "Latitude": 12.9775, "Longitude": 77.5725, "Crime_Category": "Theft"}
            ]
        }
        res = self.client.post("/api/spatial/clusters", json=post_payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("geojson", data)
        self.assertEqual(data["geojson"]["metadata"]["cluster_count"], 1)

    def test_spatial_heatmap_endpoint(self):
        post_payload = {
            "records": [
                {"case_id": "C-1", "Latitude": 12.9778, "Longitude": 77.5728, "Crime_Category": "Robbery"},
                {"case_id": "C-2", "Latitude": 12.9780, "Longitude": 77.5730, "Crime_Category": "Burglary"}
            ]
        }
        res = self.client.post("/api/spatial/heatmap", json=post_payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["count"], 2)


if __name__ == "__main__":
    unittest.main()
