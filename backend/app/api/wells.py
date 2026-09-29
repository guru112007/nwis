from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Well, WellSurvey
from app.schemas import WellSchema, WellSurveyBase
from app.engine.mcm import MinimumCurvatureMethod

router = APIRouter(prefix="/api/v1/wells", tags=["wells"])

@router.get("", response_model=List[WellSchema])
def get_all_wells(db: Session = Depends(get_db)):
    """
    Returns metadata for all wells (active and offset wells).
    """
    wells = db.query(Well).all()
    return wells

@router.get("/{well_id}", response_model=WellSchema)
def get_well_by_id(well_id: str, db: Session = Depends(get_db)):
    well = db.query(Well).filter(Well.id == well_id).first()
    if not well:
        raise HTTPException(status_code=404, detail="Well not found")
    return well

@router.get("/{well_id}/trajectory", response_model=List[WellSurveyBase])
def get_well_trajectory(well_id: str, db: Session = Depends(get_db)):
    """
    Returns full 3D directional survey trajectory calculated via Minimum Curvature Method (MCM).
    """
    well = db.query(Well).filter(Well.id == well_id).first()
    if not well:
        raise HTTPException(status_code=404, detail="Well not found")

    surveys = db.query(WellSurvey).filter(WellSurvey.well_id == well_id).order_by(WellSurvey.md.asc()).all()
    if not surveys:
        return []

    station_dicts = [{"md": s.md, "inc": s.inc, "az": s.az} for s in surveys]
    computed = MinimumCurvatureMethod.compute_full_trajectory(station_dicts, kb_elevation=well.kb_elevation)
    return computed
