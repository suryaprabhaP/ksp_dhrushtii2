"""
KSP Sentinel AI — Spatial Analytics & Hotspot Detection Engine (SOLID Compliant)
================================================================================
Zero C-extensions, Zero heavy dependencies (Zero shapely / sklearn / numpy).
Responsible exclusively for:
1. Delegating spatial clustering to QuickML cloud inference with pure Python fallback (SRP + DIP).
2. Constructing valid GeoJSON bounding polygons via pure Python Convex Hull / buffer geometries (LSP).
3. Computing cluster-level intelligence (incident counts, dominant crimes, peak hours, threat levels).
4. Generating density-weighted coordinate payloads for Heatmap rendering.
"""

import math
import logging
from collections import Counter
from typing import Dict, List, Optional, Tuple, Any

from app.core.algorithms.convex_hull import generate_buffered_polygon
from app.services.quickml_service import quickml_service

log = logging.getLogger("spatial.analytics")


class SpatialAnalyticsService:
    """
    Algorithmic Engine for Spatial Analytics & Hotspot Detection (SRP + OCP + DIP)
    """

    @staticmethod
    def _extract_coordinates_and_records(
        records: List[Dict[str, Any]],
        crime_filter: Optional[str] = None,
        division_filter: Optional[str] = None,
        station_filter: Optional[str] = None
    ) -> Tuple[List[List[float]], List[Dict[str, Any]]]:
        """
        Filters records and extracts lat/lon coordinate pairs without numpy/pandas.
        """
        valid_coords: List[List[float]] = []
        valid_records: List[Dict[str, Any]] = []

        crime_filter_lower = crime_filter.strip().lower() if crime_filter and crime_filter != "ALL" else None
        div_filter_lower = division_filter.strip().lower() if division_filter and division_filter != "ALL" else None
        stn_filter_lower = station_filter.strip().lower() if station_filter and station_filter != "ALL" else None

        for rec in records:
            # 1. Attribute filtering
            if crime_filter_lower:
                c_cat = str(rec.get("Crime_Category") or rec.get("crime_category") or rec.get("Category") or rec.get("crime_type") or "").strip().lower()
                if c_cat != crime_filter_lower:
                    continue

            if div_filter_lower:
                div = str(rec.get("Division") or rec.get("division") or rec.get("nearest_city") or "").strip().lower()
                if div != div_filter_lower:
                    continue

            if stn_filter_lower:
                stn = str(rec.get("Police_Station") or rec.get("police_station") or rec.get("station") or "").strip().lower()
                if stn != stn_filter_lower:
                    continue

            # 2. Extract Lat & Lon
            lat_val = rec.get("Latitude") or rec.get("latitude") or rec.get("lat") or rec.get("y")
            lon_val = rec.get("Longitude") or rec.get("longitude") or rec.get("lon") or rec.get("lng") or rec.get("x")

            try:
                lat = float(lat_val)
                lon = float(lon_val)
                if not (math.isnan(lat) or math.isnan(lon) or (lat == 0.0 and lon == 0.0)):
                    valid_coords.append([lat, lon])
                    valid_records.append(rec)
            except (ValueError, TypeError):
                continue

        return valid_coords, valid_records

    @classmethod
    def detect_hotspots_dbscan(
        cls,
        records: List[Dict[str, Any]],
        eps_km: float = 8.0,
        min_samples: int = 4,
        crime_filter: Optional[str] = None,
        division_filter: Optional[str] = None,
        station_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes DBSCAN clustering via QuickML / pure Python engine and converts detected clusters
        into GeoJSON polygons with metadata.
        """
        coords_list, filtered_records = cls._extract_coordinates_and_records(
            records, crime_filter=crime_filter, division_filter=division_filter, station_filter=station_filter
        )

        total_points = len(coords_list)
        if total_points < min_samples:
            return {
                "type": "FeatureCollection",
                "features": [],
                "metadata": {
                    "total_points": total_points,
                    "clustered_points": 0,
                    "noise_points": total_points,
                    "cluster_count": 0,
                    "eps_km": eps_km,
                    "min_samples": min_samples,
                    "inference_source": "insufficient_points"
                }
            }

        # Predict cluster labels via QuickML Service (with pure Python fallback)
        labels, source = quickml_service.predict_spatial_clusters(
            coords_lat_lon=coords_list,
            eps_km=eps_km,
            min_samples=min_samples
        )

        unique_labels = set(labels)
        unique_labels.discard(-1)  # -1 represents noise points in DBSCAN

        features = []
        total_clustered = 0

        # Group records by cluster label
        clusters_map: Dict[int, List[Dict[str, Any]]] = {label: [] for label in unique_labels}
        coords_map: Dict[int, List[List[float]]] = {label: [] for label in unique_labels}

        for idx, label in enumerate(labels):
            if label != -1:
                clusters_map[label].append(filtered_records[idx])
                coords_map[label].append(coords_list[idx])
                total_clustered += 1

        # Generate GeoJSON Polygon Feature for each cluster using pure Python Graham Scan / buffer
        cluster_list = []
        for label, cluster_pts in coords_map.items():
            cluster_recs = clusters_map[label]
            cluster_info = cls._build_cluster_feature(label, cluster_pts, cluster_recs, eps_km)
            cluster_list.append(cluster_info)

        # Sort clusters by incident count descending
        cluster_list.sort(key=lambda f: f["properties"]["incident_count"], reverse=True)

        # Re-number ranking (Hotspot #1, Hotspot #2, etc.)
        for rank, feature in enumerate(cluster_list, start=1):
            feature["properties"]["rank"] = rank
            feature["properties"]["name"] = f"Hotspot #{rank} ({feature['properties']['primary_crime']})"
            features.append(feature)

        noise_count = sum(1 for l in labels if l == -1)

        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "total_points": total_points,
                "clustered_points": total_clustered,
                "noise_points": noise_count,
                "cluster_count": len(features),
                "eps_km": eps_km,
                "min_samples": min_samples,
                "crime_filter": crime_filter or "ALL",
                "inference_source": source
            }
        }

    @classmethod
    def _build_cluster_feature(
        cls,
        label: int,
        pts: List[List[float]],
        records: List[Dict[str, Any]],
        eps_km: float
    ) -> Dict[str, Any]:
        """
        Constructs a single GeoJSON Feature representing a cluster boundary + statistical intelligence.
        Uses pure Python convex hull / buffer generation.
        """
        # Generate Polygon Geometry via Pure Python Convex Hull
        geojson_geometry = generate_buffered_polygon(pts, eps_km=eps_km)

        # Compute centroid [lat, lon]
        centroid_lat = sum(p[0] for p in pts) / len(pts)
        centroid_lon = sum(p[1] for p in pts) / len(pts)

        # Compute statistics & metadata
        crime_categories = []
        stations = []
        statuses = []
        for r in records:
            cat = r.get("Crime_Category") or r.get("crime_category") or r.get("Category") or r.get("crime_type") or "General"
            stn = r.get("Police_Station") or r.get("police_station") or r.get("station") or r.get("nearest_city") or "Local Station"
            stat = r.get("Status") or r.get("status") or r.get("case_status") or "Open"
            crime_categories.append(str(cat))
            stations.append(str(stn))
            statuses.append(str(stat))

        cat_counts = Counter(crime_categories)
        stn_counts = Counter(stations)
        primary_crime, primary_count = cat_counts.most_common(1)[0] if cat_counts else ("General", len(records))
        top_station = stn_counts.most_common(1)[0][0] if stn_counts else "Jurisdiction Area"

        incident_count = len(records)

        # Threat Level Grading
        if incident_count >= 25 or (incident_count >= 10 and primary_crime in ["Robbery", "Extortion", "Assault"]):
            threat_level = "CRITICAL"
            threat_color = "#ef4444"  # Crimson
        elif incident_count >= 10:
            threat_level = "HIGH"
            threat_color = "#f97316"  # Orange
        else:
            threat_level = "MODERATE"
            threat_color = "#eab308"  # Yellow

        properties = {
            "cluster_id": f"cluster_{label}",
            "incident_count": incident_count,
            "primary_crime": primary_crime,
            "primary_crime_share": round((primary_count / max(1, incident_count)) * 100, 1),
            "threat_level": threat_level,
            "threat_color": threat_color,
            "centroid": [round(centroid_lat, 5), round(centroid_lon, 5)],
            "top_station": top_station,
            "category_breakdown": dict(cat_counts),
            "station_breakdown": dict(stn_counts),
            "status_breakdown": dict(Counter(statuses)),
            "sample_cases": [
                {
                    "case_id": r.get("case_id") or r.get("FIR_Number") or r.get("id") or f"CASE-{i+1}",
                    "crime": r.get("Crime_Category") or r.get("crime_type") or "Incident",
                    "date": r.get("incident_date") or r.get("Date") or "Recent",
                    "lat": r.get("latitude") or r.get("Latitude"),
                    "lon": r.get("longitude") or r.get("Longitude")
                }
                for i, r in enumerate(records[:8])
            ],
            "llm_investigative_leads": [
                f"Concentration of {incident_count} cases under {top_station} jurisdiction with {primary_crime} dominant ({round((primary_count / max(1, incident_count)) * 100)}%).",
                f"Check common suspects, modus operandi, and vehicle links within {eps_km} km radius.",
                f"Cross-reference patrol route schedules during peak activity windows."
            ]
        }

        return {
            "type": "Feature",
            "geometry": geojson_geometry,
            "properties": properties
        }

    @classmethod
    def generate_heatmap_payload(
        cls,
        records: List[Dict[str, Any]],
        crime_filter: Optional[str] = None,
        division_filter: Optional[str] = None,
        station_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extracts weighted lat/lon points suitable for rendering continuous density heatmaps.
        Returns: { "points": [[lat, lon, weight], ...], "count": int }
        """
        coords_list, filtered_records = cls._extract_coordinates_and_records(
            records, crime_filter=crime_filter, division_filter=division_filter, station_filter=station_filter
        )

        heatmap_points = []
        for idx, coord in enumerate(coords_list):
            rec = filtered_records[idx]
            crime_cat = str(rec.get("Crime_Category") or rec.get("crime_type") or "").lower()
            if any(k in crime_cat for k in ["robbery", "extortion", "assault", "murder"]):
                weight = 1.0
            elif any(k in crime_cat for k in ["burglary", "theft"]):
                weight = 0.75
            else:
                weight = 0.5

            heatmap_points.append([round(float(coord[0]), 5), round(float(coord[1]), 5), weight])

        return {
            "success": True,
            "count": len(heatmap_points),
            "points": heatmap_points
        }


# Singleton instance export
spatial_analytics_service = SpatialAnalyticsService()
