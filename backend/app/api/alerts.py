import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Well, OperationalEvent, AlertFeedback
from app.schemas import LookAheadAlert, AlertFeedbackRequest
from app.engine.alert_engine import LookAheadAlertEngine

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])

@router.get("/lookahead", response_model=List[LookAheadAlert])
def get_lookahead_alerts(
    active_well_id: str = "NH-24",
    active_md_m: float = 2100.0,
    db: Session = Depends(get_db)
):
    """
    Evaluates 3-tier look-ahead alerts for a given active well and bit depth MD.
    """
    active_well = db.query(Well).filter(Well.id == active_well_id).first()
    if not active_well:
        raise HTTPException(status_code=404, detail="Active well not found")

    active_well_dict = {
        "id": active_well.id,
        "surface_lat": active_well.surface_lat,
        "surface_lon": active_well.surface_lon
    }

    offset_wells = db.query(Well).filter(Well.id != active_well_id).all()
    offset_wells_dicts = [{"id": w.id, "surface_lat": w.surface_lat, "surface_lon": w.surface_lon} for w in offset_wells]

    offset_events = db.query(OperationalEvent).all()
    offset_events_dicts = [
        {
            "id": e.id,
            "well_id": e.well_id,
            "md": e.md,
            "tvd": e.tvd,
            "tvdss": e.tvdss,
            "formation": e.formation,
            "event_category": e.event_category,
            "severity": e.severity,
            "summary": e.summary,
            "mitigation": e.mitigation,
            "source_file": e.source_file,
            "source_page": e.source_page,
            "bbox": e.bbox,
            "doc_hash": e.doc_hash,
            "verified_by_human": e.verified_by_human,
            "ocr_confidence": e.ocr_confidence
        }
        for e in offset_events
    ]

    active_tvdss = active_md_m * 0.95 - active_well.kb_elevation

    engine = LookAheadAlertEngine()
    alerts = engine.evaluate_active_bit(
        active_well=active_well_dict,
        active_bit_md=active_md_m,
        active_bit_tvdss=active_tvdss,
        current_formation="Tipam Sandstone",
        offset_wells=offset_wells_dicts,
        offset_events=offset_events_dicts
    )

    return alerts

@router.post("/feedback")
def record_alert_feedback(payload: AlertFeedbackRequest, db: Session = Depends(get_db)):
    """
    Records user feedback ("USEFUL" or "DISMISSED") for a triggered alert.
    """
    fb = AlertFeedback(
        alert_id=payload.alert_id,
        user_action=payload.user_action,
        comments=payload.comments,
        timestamp=datetime.datetime.utcnow()
    )
    db.add(fb)
    db.commit()
    return {"status": "success", "alert_id": payload.alert_id, "user_action": payload.user_action}
