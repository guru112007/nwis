from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import OperationalEvent
from app.schemas import OperationalEventSchema

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

@router.get("/review-queue", response_model=List[OperationalEventSchema])
def get_reviewer_queue(db: Session = Depends(get_db)):
    """
    Returns extracted event records with OCR confidence < 0.85 for human verification.
    """
    events = db.query(OperationalEvent).filter(
        (OperationalEvent.ocr_confidence < 0.85) | (OperationalEvent.verified_by_human == False)
    ).all()
    return events

@router.post("/{event_id}/verify")
def verify_document_event(event_id: int, db: Session = Depends(get_db)):
    """
    Human reviewer one-click verification for low-confidence OCR records.
    """
    evt = db.query(OperationalEvent).filter(OperationalEvent.id == event_id).first()
    if not evt:
        raise HTTPException(status_code=404, detail="Operational event record not found")

    evt.verified_by_human = True
    evt.ocr_confidence = 0.99
    db.commit()
    return {"status": "verified", "event_id": event_id, "verified_by_human": True}

@router.get("/download/{source_file}")
def download_pdf_report(source_file: str):
    """
    Serves PDF report document for the in-app preview reader.
    """
    data_dir = Path(__file__).resolve().parent.parent.parent.parent / "data" / "reports"
    filepath = data_dir / source_file

    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"PDF document {source_file} not found")

    return FileResponse(filepath, media_type="application/pdf", filename=source_file)
