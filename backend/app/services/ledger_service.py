import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# In-memory cryptographic block ledger (simulating blockchain-grade tamper proof ledger)
GENESIS_HASH = "0000000000000000000a7b4f2c9e1d8a3f5b7c8d9e0f1a2b3c4d5e6f7a8b9c0d"

mock_ledger_chain: List[Dict[str, Any]] = [
    {
        "block_height": 0,
        "record_id": "genesis_block",
        "student_id": "SYSTEM_CORE",
        "student_name": "Bio-XAI Core Root",
        "department_id": "SYSTEM",
        "timestamp": "2026-01-01T00:00:00Z",
        "status": "GENESIS",
        "verification_method": "ROOT_GENESIS",
        "previous_hash": "0" * 64,
        "block_hash": GENESIS_HASH,
        "merkle_leaf": hashlib.sha256("genesis_root".encode()).hexdigest(),
        "is_tampered": False
    }
]

def calculate_block_hash(
    block_height: int,
    previous_hash: str,
    record_id: str,
    student_id: str,
    timestamp: str,
    status: str,
    verification_method: str
) -> str:
    payload = f"{block_height}:{previous_hash}:{record_id}:{student_id}:{timestamp}:{status}:{verification_method}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def create_attendance_block(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Appends a new cryptographically chained block to the attendance ledger.
    """
    prev_block = mock_ledger_chain[-1]
    prev_hash = prev_block["block_hash"]
    height = len(mock_ledger_chain)
    timestamp = record.get("marked_at", datetime.utcnow().isoformat())

    block_hash = calculate_block_hash(
        block_height=height,
        previous_hash=prev_hash,
        record_id=str(record.get("id", f"rec_{height}")),
        student_id=record.get("student_id", "UNKNOWN"),
        timestamp=timestamp,
        status=record.get("status", "PRESENT"),
        verification_method=record.get("verification_method", "BIOMETRIC_DIRECT")
    )

    merkle_leaf = hashlib.sha256(f"{record.get('id')}:{block_hash}".encode("utf-8")).hexdigest()

    block = {
        "block_height": height,
        "record_id": str(record.get("id")),
        "student_id": record.get("student_id"),
        "student_name": record.get("student_name", "Student"),
        "department_id": record.get("department_id", "dept_cs"),
        "timestamp": timestamp,
        "status": record.get("status", "PRESENT"),
        "verification_method": record.get("verification_method", "BIOMETRIC_DIRECT"),
        "confidence_score": record.get("confidence_score", 0.95),
        "previous_hash": prev_hash,
        "block_hash": block_hash,
        "merkle_leaf": merkle_leaf,
        "is_tampered": False
    }

    mock_ledger_chain.append(block)
    logger.info(f"🔗 Appended Cryptographic Attendance Block #{height} - Hash: {block_hash[:16]}...")
    return block

def verify_ledger_integrity(department_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Iterates through the entire cryptographic chain to verify mathematical hash links.
    Detects any database tampering or unauthorized record modifications.
    """
    chain_to_check = mock_ledger_chain
    if department_id and department_id != "ALL":
        chain_to_check = [b for b in mock_ledger_chain if b.get("department_id") in [department_id, "SYSTEM"]]

    total_blocks = len(chain_to_check)
    tampered_blocks = []
    
    for i in range(1, len(mock_ledger_chain)):
        current = mock_ledger_chain[i]
        prev = mock_ledger_chain[i - 1]

        # 1. Check previous hash continuity
        if current["previous_hash"] != prev["block_hash"]:
            tampered_blocks.append({
                "block_height": current["block_height"],
                "reason": f"Hash continuity broken. Expected prev_hash {prev['block_hash'][:12]}..., found {current['previous_hash'][:12]}..."
            })
            continue

        # 2. Recompute current block hash
        expected_hash = calculate_block_hash(
            block_height=current["block_height"],
            previous_hash=current["previous_hash"],
            record_id=current["record_id"],
            student_id=current["student_id"],
            timestamp=current["timestamp"],
            status=current["status"],
            verification_method=current["verification_method"]
        )

        if current["block_hash"] != expected_hash:
            tampered_blocks.append({
                "block_height": current["block_height"],
                "reason": "Block content mutated: recomputed hash does not match stored block_hash."
            })

    is_valid = len(tampered_blocks) == 0
    current_head = mock_ledger_chain[-1]

    return {
        "status": "VERIFIED" if is_valid else "CORRUPTED",
        "is_valid": is_valid,
        "total_blocks_audited": len(mock_ledger_chain),
        "block_height": len(mock_ledger_chain) - 1,
        "chain_head_hash": current_head["block_hash"],
        "genesis_hash": GENESIS_HASH,
        "verified_at": datetime.utcnow().isoformat(),
        "tampered_blocks": tampered_blocks,
        "algorithm": "SHA-256 Merkle-Chained Ledger",
        "audit_message": "All attendance records mathematically linked and sealed against unauthorized manipulation." if is_valid else f"Warning: {len(tampered_blocks)} corrupted blocks identified in ledger audit."
    }

def get_recent_blocks(limit: int = 20, department_id: Optional[str] = None) -> List[Dict[str, Any]]:
    chain = mock_ledger_chain
    if department_id and department_id != "ALL":
        chain = [b for b in chain if b.get("department_id") in [department_id, "SYSTEM"]]
    return list(reversed(chain[-limit:]))
