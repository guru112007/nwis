from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Well, OperationalEvent, WellSurvey
from app.schemas import BacktestMetrics
from app.engine.backtest import HistoricalBacktestEngine

router = APIRouter(prefix="/api/v1/backtest", tags=["backtest"])

@router.get("/run", response_model=BacktestMetrics)
def run_historical_backtest(db: Session = Depends(get_db)):
    """
    Executes historical backtest harness validating spatial engine across historical wells.
    Returns Hit Rate (%), Median Lead Distance (m), and False Alert Rate per 1,000m.
    """
    wells = db.query(Well).all()
    wells_dicts = [
        {"id": w.id, "surface_lat": w.surface_lat, "surface_lon": w.surface_lon}
        for w in wells
    ]

    events = db.query(OperationalEvent).all()
    events_dicts = [
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
        for e in events
    ]

    surveys_dict = {}
    for w in wells:
        surveys = db.query(WellSurvey).filter(WellSurvey.well_id == w.id).order_by(WellSurvey.md.asc()).all()
        surveys_dict[w.id] = [{"md": s.md, "tvdss": s.tvdss} for s in surveys]

    metrics = HistoricalBacktestEngine.run_backtest(
        historical_wells=wells_dicts,
        historical_events=events_dicts,
        historical_surveys=surveys_dict
    )

    return metrics
