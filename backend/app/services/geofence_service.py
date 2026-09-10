import math
import logging
from typing import List, Dict
from shapely.geometry import Point, Polygon
from app.models.schemas import Coordinate

logger = logging.getLogger(__name__)

def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculates the great-circle distance between two points in meters using Haversine formula.
    """
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)

    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def is_point_in_polygon(lat: float, lng: float, polygon_coords: List[Dict[str, float]]) -> bool:
    """
    Validates whether GPS (lat, lng) falls inside a multi-point polygon boundary.
    polygon_coords: list of dicts [{'lat': y, 'lng': x}, ...]
    """
    if not polygon_coords or len(polygon_coords) < 3:
        return False
    try:
        # Shapely uses (lng, lat) for (x, y) coordinates
        poly_points = [(c['lng'], c['lat']) for c in polygon_coords]
        polygon = Polygon(poly_points)
        point = Point(lng, lat)
        return polygon.contains(point) or polygon.touches(point)
    except Exception as e:
        logger.error(f"Point in polygon check failed: {e}")
        return False

def check_geofence(lat: float, lng: float, geofence_zone: dict) -> bool:
    """
    Dual validation:
    1. Polygon inclusion if polygon coordinates are present.
    2. Haversine distance check against center point + radius.
    Returns True if either check succeeds.
    """
    if not geofence_zone:
        return True  # If no geofence zone configured, default allow

    # Check 1: Polygon check
    coords = geofence_zone.get("coordinates", [])
    if coords and len(coords) >= 3:
        if is_point_in_polygon(lat, lng, coords):
            return True

    # Check 2: Radius check against center
    center_lat = geofence_zone.get("center_lat")
    center_lng = geofence_zone.get("center_lng")
    radius = geofence_zone.get("radius_meters", 150.0)

    if center_lat is not None and center_lng is not None:
        dist = haversine_distance(lat, lng, center_lat, center_lng)
        if dist <= radius:
            return True

    return False
