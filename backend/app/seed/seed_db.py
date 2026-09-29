import os
import hashlib
from pathlib import Path
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models import Well, WellSurvey, FormationTop, LogCurve, OperationalEvent, AlertFeedback
from app.seed.assam_generator import (
    UPPER_ASSAM_WELLS,
    STRATIGRAPHY_TOPS,
    HISTORICAL_INCIDENTS,
    generate_directional_surveys,
    generate_log_curves,
    generate_pdf_report_files
)
from app.engine.embeddings import generate_embedding

def seed_database():
    """
    Seeds database with Upper Assam shelf wells, 3D surveys, stratigraphy tops, log curves,
    operational events with 384-dim vector embeddings, and PDF reports.
    """
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    print("Seeding database with Upper Assam Shelf synthetic dataset...")

    # Clear existing data
    db.query(AlertFeedback).delete()
    db.query(OperationalEvent).delete()
    db.query(LogCurve).delete()
    db.query(FormationTop).delete()
    db.query(WellSurvey).delete()
    db.query(Well).delete()
    db.commit()

    # Generate PDF reports in data/reports
    data_dir = Path(__file__).resolve().parent.parent.parent.parent / "data"
    generate_pdf_report_files(data_dir)

    # 1. Insert Wells
    for w_meta in UPPER_ASSAM_WELLS:
        well = Well(
            id=w_meta["id"],
            name=w_meta["name"],
            surface_lat=w_meta["surface_lat"],
            surface_lon=w_meta["surface_lon"],
            kb_elevation=w_meta["kb_elevation"],
            water_depth=w_meta["water_depth"],
            is_synthetic=w_meta["is_synthetic"],
            field_name=w_meta["field_name"],
            operator=w_meta["operator"]
        )
        db.add(well)
        db.flush()

        # 2. Directional Surveys
        surveys = generate_directional_surveys(w_meta)
        for s in surveys:
            survey_obj = WellSurvey(
                well_id=w_meta["id"],
                md=s["md"],
                inc=s["inc"],
                az=s["az"],
                tvd=s["tvd"],
                tvdss=s["tvdss"],
                dx_north=s["dx_north"],
                dy_east=s["dy_east"]
            )
            db.add(survey_obj)

        # 3. Formation Tops
        kb = w_meta["kb_elevation"]
        for top_name, top_md in STRATIGRAPHY_TOPS:
            # Estimate TVDSS top = MD * 0.95 - KB
            tvdss_top = top_md * 0.95 - kb
            ft_obj = FormationTop(
                well_id=w_meta["id"],
                formation_name=top_name,
                md_top=top_md,
                tvdss_top=tvdss_top
            )
            db.add(ft_obj)

        # 4. Log Curves
        log_points = generate_log_curves(w_meta["id"], w_meta["max_md"])
        for lp in log_points:
            log_obj = LogCurve(
                well_id=w_meta["id"],
                md=lp["md"],
                gr=lp["gr"],
                res=lp["res"],
                dt=lp["dt"]
            )
            db.add(log_obj)

    db.commit()

    # 5. Insert Operational Events with 384-dim Embeddings
    for inc in HISTORICAL_INCIDENTS:
        text_for_embed = f"{inc['event_category']} in {inc['formation']}: {inc['summary']} Mitigation: {inc['mitigation']}"
        embed_vec = generate_embedding(text_for_embed)

        doc_hash = hashlib.sha256(inc["source_file"].encode()).hexdigest()

        evt_obj = OperationalEvent(
            well_id=inc["well_id"],
            md=inc["md"],
            tvd=inc["tvd"],
            tvdss=inc["tvdss"],
            formation=inc["formation"],
            event_category=inc["event_category"],
            severity=inc["severity"],
            summary=inc["summary"],
            mitigation=inc["mitigation"],
            embedding=embed_vec,
            source_file=inc["source_file"],
            source_page=inc["source_page"],
            bbox=inc["bbox"],
            doc_hash=doc_hash,
            verified_by_human=inc["verified_by_human"],
            ocr_confidence=inc["ocr_confidence"]
        )
        db.add(evt_obj)

    db.commit()
    db.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
