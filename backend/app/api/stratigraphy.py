from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LogCurve, FormationTop
from app.schemas import LogCurvePoint
from app.config import STRATIGRAPHY_CONFIG

router = APIRouter(prefix="/api/v1/stratigraphy", tags=["stratigraphy"])

@router.get("")
def get_stratigraphy_sequence():
    """
    Returns configured Upper Assam shelf stratigraphic sequence and risk profile.
    """
    return STRATIGRAPHY_CONFIG.get("stratigraphy", [])

@router.get("/logs/{well_id}", response_model=List[LogCurvePoint])
def get_well_logs(well_id: str, db: Session = Depends(get_db)):
    """
    Returns GR, RES, DT log curves for a well indexed by MD and TVDSS.
    """
    logs = db.query(LogCurve).filter(LogCurve.well_id == well_id).order_by(LogCurve.md.asc()).all()
    return logs
