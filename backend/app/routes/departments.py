from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.schemas import DepartmentCreate, DepartmentResponse, UserRole, TokenData
from app.services.auth_service import get_current_user, require_roles
from app.routes.users_data import mock_departments_db, mock_users_db

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.get("", response_model=List[DepartmentResponse])
async def list_departments(current_user: TokenData = Depends(get_current_user)):
    results = []
    for dept in mock_departments_db.values():
        hod_name = "Unassigned"
        if dept.get("hod_id"):
            hod = next((u for u in mock_users_db.values() if u["id"] == dept["hod_id"]), None)
            if hod:
                hod_name = hod["name"]

        # Calculate counts
        student_count = len([u for u in mock_users_db.values() if u["role"] == UserRole.STUDENT and u.get("department_id") == dept["id"]])
        mentor_count = len([u for u in mock_users_db.values() if u["role"] == UserRole.MENTOR and u.get("department_id") == dept["id"]])

        results.append({
            "id": dept["id"],
            "name": dept["name"],
            "code": dept["code"],
            "hod_id": dept.get("hod_id"),
            "hod_name": hod_name,
            "student_count": student_count,
            "mentor_count": mentor_count
        })
    return results

@router.post("", response_model=DepartmentResponse)
async def create_department(
    dept_data: DepartmentCreate,
    current_user: TokenData = Depends(require_roles([UserRole.ADMIN]))
):
    new_id = f"dept_{len(mock_departments_db) + 1}"
    dept_entry = {
        "id": new_id,
        "name": dept_data.name,
        "code": dept_data.code,
        "hod_id": dept_data.hod_id
    }
    mock_departments_db[new_id] = dept_entry
    return {
        "id": new_id,
        "name": dept_data.name,
        "code": dept_data.code,
        "hod_id": dept_data.hod_id,
        "hod_name": "Unassigned",
        "student_count": 0,
        "mentor_count": 0
    }
