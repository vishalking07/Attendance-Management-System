from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.schemas import GeofenceZoneCreate, GeofenceZoneResponse, UserRole, TokenData
from app.services.auth_service import get_current_user, require_roles
from app.routes.users_data import mock_geofence_db

router = APIRouter(prefix="/geofence", tags=["Geofence"])

@router.get("", response_model=List[GeofenceZoneResponse])
async def list_geofence_zones(current_user: TokenData = Depends(get_current_user)):
    return list(mock_geofence_db.values())

@router.post("", response_model=GeofenceZoneResponse)
async def create_geofence_zone(
    zone_data: GeofenceZoneCreate,
    current_user: TokenData = Depends(require_roles([UserRole.ADMIN]))
):
    new_id = f"geo_{len(mock_geofence_db) + 1}"
    coords_dict = [{"lat": c.lat, "lng": c.lng} for c in zone_data.coordinates]
    zone_entry = {
        "id": new_id,
        "name": zone_data.name,
        "department_id": zone_data.department_id,
        "coordinates": coords_dict,
        "center_lat": zone_data.center_lat,
        "center_lng": zone_data.center_lng,
        "radius_meters": zone_data.radius_meters
    }
    mock_geofence_db[new_id] = zone_entry
    return zone_entry
