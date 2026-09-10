from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from app.models.schemas import UserRole, TokenData
from app.services.auth_service import get_current_user
from app.services.ledger_service import get_recent_blocks, verify_ledger_integrity
from app.services.anomaly_service import get_department_anomaly_queue

router = APIRouter(prefix="/ledger", tags=["Cryptographic Ledger & Anomalies"])

@router.get("/blocks")
async def get_ledger_blocks(
    limit: int = 20,
    department_id: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Returns recent cryptographically chained blocks for the audit ledger.
    """
    blocks = get_recent_blocks(limit=limit, department_id=department_id)
    return blocks

@router.post("/verify")
async def verify_chain_integrity(
    department_id: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Executes a complete SHA-256 mathematical hash verification across the ledger.
    """
    verification_result = verify_ledger_integrity(department_id=department_id)
    return verification_result

@router.get("/anomalies")
async def get_anomaly_radar(
    current_user: TokenData = Depends(get_current_user)
):
    """
    Returns flagged proxy anomalies and borderline geofence check-ins.
    """
    return get_department_anomaly_queue()
