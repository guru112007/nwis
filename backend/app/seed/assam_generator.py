import os
import hashlib
from pathlib import Path
import numpy as np
from typing import List, Dict, Any

from app.engine.mcm import MinimumCurvatureMethod
from app.engine.embeddings import generate_embedding

UPPER_ASSAM_WELLS = [
    {
        "id": "NH-24",
        "name": "Nahorkatiya-24 (Active Well)",
        "surface_lat": 27.4850,
        "surface_lon": 95.3400,
        "kb_elevation": 102.5,
        "water_depth": 0.0,
        "is_synthetic": True,
        "field_name": "Nahorkatiya",
        "operator": "Oil India Limited (OIL)",
        "max_md": 3500.0,
        "build_inc": 22.5,
        "azimuth": 45.0
    },
    {
        "id": "NH-02",
        "name": "Nahorkatiya-02 (Offset)",
        "surface_lat": 27.4880,
        "surface_lon": 95.3420,
        "kb_elevation": 101.8,
        "water_depth": 0.0,
        "is_synthetic": True,
        "field_name": "Nahorkatiya",
        "operator": "Oil India Limited (OIL)",
        "max_md": 3400.0,
        "build_inc": 18.0,
        "azimuth": 50.0
    },
    {
        "id": "NH-09",
        "name": "Nahorkatiya-09 (Offset)",
        "surface_lat": 27.4810,
        "surface_lon": 95.3370,
        "kb_elevation": 103.1,
        "water_depth": 0.0,
        "is_synthetic": True,
        "field_name": "Nahorkatiya",
        "operator": "Oil India Limited (OIL)",
        "max_md": 3600.0,
        "build_inc": 25.0,
        "azimuth": 40.0
    },
    {
        "id": "NH-15",
        "name": "Nahorkatiya-15 (Offset)",
        "surface_lat": 27.4910,
        "surface_lon": 95.3460,
        "kb_elevation": 100.5,
        "water_depth": 0.0,
        "is_synthetic": True,
        "field_name": "Nahorkatiya",
        "operator": "Oil India Limited (OIL)",
        "max_md": 3700.0,
        "build_inc": 15.0,
        "azimuth": 60.0
    },
    {
        "id": "JLN-04",
        "name": "Jalannagar-04 (Offset)",
        "surface_lat": 27.4750,
        "surface_lon": 95.3300,
        "kb_elevation": 99.2,
        "water_depth": 0.0,
        "is_synthetic": True,
        "field_name": "Jalannagar",
        "operator": "Oil India Limited (OIL)",
        "max_md": 3500.0,
        "build_inc": 20.0,
        "azimuth": 35.0
    },
    {
        "id": "BGB-12",
        "name": "Boghapani-12 (Offset)",
        "surface_lat": 27.4650,
        "surface_lon": 95.3200,
        "kb_elevation": 104.0,
        "water_depth": 0.0,
        "is_synthetic": True,
        "field_name": "Boghapani",
        "operator": "Oil India Limited (OIL)",
        "max_md": 3300.0,
        "build_inc": 12.0,
        "azimuth": 30.0
    }
]

STRATIGRAPHY_TOPS = [
    ("Alluvium", 0.0),
    ("Dhekiajuli", 250.0),
    ("Girujan Clay", 800.0),
    ("Tipam Sandstone", 1650.0),
    ("Barail Sand/Coal", 2500.0),
    ("Kopili Shale", 3200.0)
]

HISTORICAL_INCIDENTS = [
    {
        "well_id": "NH-02",
        "md": 2150.0,
        "tvd": 2046.8,
        "tvdss": 1945.0,
        "formation": "Tipam Sandstone",
        "event_category": "Severe Mud Loss",
        "severity": "L2",
        "summary": "Encountered high permeability vuggy sandstone zone in Tipam formation. Complete mud returns lost at 35 bbl/hr rate. Standpipe pressure dropped by 180 psi.",
        "mitigation": "Pumped 45 bbl high-viscosity LCM pill (Nutplug + Mica 30 ppb). Reduced flow rate from 650 GPM to 520 GPM and reduced ROP to 6.5 m/hr. Returns recovered to 92%.",
        "source_file": "NH-02_DDR_Phase3_Tipam.pdf",
        "source_page": 14,
        "bbox": [72.0, 140.0, 520.0, 310.0],
        "verified_by_human": True,
        "ocr_confidence": 0.98
    },
    {
        "well_id": "NH-09",
        "md": 2780.0,
        "tvd": 2645.1,
        "tvdss": 2542.0,
        "formation": "Barail Sand/Coal",
        "event_category": "Differential Pipe Sticking",
        "severity": "L3",
        "summary": "While drilling coal seam section in Barail formation, drill string experienced static differential sticking during connection at 2780m MD. Overpull exceeded 85,000 lbs.",
        "mitigation": "Spotted 25 bbl organic pipe-freeing fluid (pipe lube). Jarred downwards with maximum trip margin for 4.5 hours. String freed successfully. Mud weight increased by +0.04 SG.",
        "source_file": "NH-09_WCR_Barail_Section.pdf",
        "source_page": 28,
        "bbox": [65.0, 180.0, 530.0, 360.0],
        "verified_by_human": True,
        "ocr_confidence": 0.95
    },
    {
        "well_id": "JLN-04",
        "md": 2920.0,
        "tvd": 2774.2,
        "tvdss": 2675.0,
        "formation": "Barail Sand/Coal",
        "event_category": "Gas Influx / Well Control",
        "severity": "L3",
        "summary": "Gas kick encountered upon penetrating high pressure Barail sand channel. Pit volume increased by +0.8 bbl in 4 minutes. Gas chromatograph peaked at 14.5% C1.",
        "mitigation": "Immediate soft shut-in performed via Upper Annular BOP. SICP registered at 450 psi, SIDPP at 310 psi. Circulated kick out using Driller's Method with 1.34 SG kill mud.",
        "source_file": "JLN-04_Well_Control_Incident_Report.pdf",
        "source_page": 5,
        "bbox": [80.0, 120.0, 510.0, 290.0],
        "verified_by_human": True,
        "ocr_confidence": 0.97
    },
    {
        "well_id": "NH-15",
        "md": 3410.0,
        "tvd": 3265.5,
        "tvdss": 3165.0,
        "formation": "Kopili Shale",
        "event_category": "Sloughing Shale / Hole Collapse",
        "severity": "L2",
        "summary": "Brittle Kopili shale sloughing observed. Shaker screens loaded with large angular shale cavings. Torque spiked to 38,000 ft-lbs with severe drag on wiper trip.",
        "mitigation": "Increased KCl mud inhibitor to 8.5%. Elevated mud weight from 1.28 SG to 1.34 SG to stabilize hole wall. High-viscosity sweep pumped every 45m.",
        "source_file": "NH-15_DDR_Kopili_Shale.pdf",
        "source_page": 42,
        "bbox": [70.0, 200.0, 540.0, 410.0],
        "verified_by_human": True,
        "ocr_confidence": 0.94
    },
    {
        "well_id": "BGB-12",
        "md": 1980.0,
        "tvd": 1889.0,
        "tvdss": 1785.0,
        "formation": "Tipam Sandstone",
        "event_category": "Severe Mud Loss",
        "severity": "L1",
        "summary": "Partial fluid loss of 12 bbl/hr recorded in upper Tipam section. Hand-written daily report page was degraded.",
        "mitigation": "Added coarse mica pills (15 ppb) to active mud pit system. Loss rate reduced to < 3 bbl/hr.",
        "source_file": "BGB-12_Scanned_Log_Report.pdf",
        "source_page": 9,
        "bbox": [50.0, 100.0, 480.0, 250.0],
        "verified_by_human": False,  # Needs human verification queue!
        "ocr_confidence": 0.74        # < 0.85 threshold!
    }
]

def generate_directional_surveys(well_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generates realistic 3D directional survey stations for a well.
    """
    max_md = well_meta["max_md"]
    build_inc = well_meta["build_inc"]
    az = well_meta["azimuth"]

    stations = []
    # Vertical section 0 to 500m
    stations.append({"md": 0.0, "inc": 0.0, "az": az})
    stations.append({"md": 500.0, "inc": 0.0, "az": az})

    # Kickoff point KOP at 500m building to build_inc at 1500m
    for md in range(600, 1600, 200):
        inc = (md - 500) / 1000.0 * build_inc
        stations.append({"md": float(md), "inc": float(inc), "az": az})

    # Tangent section 1500m to max_md
    for md in range(1600, int(max_md) + 1, 200):
        stations.append({"md": float(md), "inc": float(build_inc), "az": az})

    # Compute full MCM trajectory
    return MinimumCurvatureMethod.compute_full_trajectory(stations, kb_elevation=well_meta["kb_elevation"])

def generate_log_curves(well_id: str, max_md: float) -> List[Dict[str, Any]]:
    """
    Generates synthetic Gamma Ray (GR), Resistivity (RES), and Sonic (DT) log curves.
    Aligned with Upper Assam stratigraphy.
    """
    logs = []
    np.random.seed(abs(hash(well_id)) % (2**32))

    for md in range(0, int(max_md) + 1, 5): # Every 5m
        # Determine formation base GR
        if md < 250:
            base_gr, base_res, base_dt = 35.0, 12.0, 110.0 # Alluvium
        elif md < 800:
            base_gr, base_res, base_dt = 50.0, 25.0, 95.0  # Dhekiajuli
        elif md < 1650:
            base_gr, base_res, base_dt = 85.0, 8.0, 120.0  # Girujan Clay
        elif md < 2500:
            base_gr, base_res, base_dt = 40.0, 45.0, 85.0  # Tipam Sandstone
        elif md < 3200:
            base_gr, base_res, base_dt = 95.0, 30.0, 100.0 # Barail Sand/Coal
        else:
            base_gr, base_res, base_dt = 120.0, 5.0, 130.0 # Kopili Shale

        noise_gr = float(np.random.normal(0, 4.0))
        noise_res = float(np.random.normal(0, 1.5))
        noise_dt = float(np.random.normal(0, 2.0))

        logs.append({
            "well_id": well_id,
            "md": float(md),
            "gr": round(max(10.0, base_gr + noise_gr), 1),
            "res": round(max(0.5, base_res + noise_res), 2),
            "dt": round(max(40.0, base_dt + noise_dt), 1)
        })

    return logs

def generate_pdf_report_files(data_dir: Path):
    """
    Generates synthetic PDF files in data/reports directory using reportlab if available,
    or HTML/text formatted mock pdf bytes.
    """
    reports_dir = data_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    for incident in HISTORICAL_INCIDENTS:
        filename = incident["source_file"]
        filepath = reports_dir / filename
        if filepath.exists():
            continue

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

            c = canvas.Canvas(str(filepath), pagesize=letter)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, 750, f"OIL INDIA LIMITED - DAILY DRILLING & INCIDENT REPORT")
            c.setFont("Helvetica", 10)
            c.drawString(50, 730, f"Well: {incident['well_id']} | Field: Upper Assam Shelf | Page {incident['source_page']}")
            c.setStrokeColorRGB(0.2, 0.4, 0.8)
            c.line(50, 720, 550, 720)

            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, 690, f"OPERATIONAL EVENT SUMMARY: {incident['event_category'].upper()}")
            c.setFont("Helvetica", 10)
            c.drawString(50, 670, f"Measured Depth: {incident['md']} m MD | TVDSS: {incident['tvdss']} m | Formation: {incident['formation']}")
            c.drawString(50, 650, f"Severity Tier: {incident['severity']} | OCR Verification Status: {'Human Verified' if incident['verified_by_human'] else 'Pending Review'}")

            # Draw incident details box
            c.setStrokeColorRGB(0.8, 0.2, 0.2)
            c.rect(50, 480, 500, 150)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(60, 610, "Incidents & Observations:")
            c.setFont("Helvetica", 9)

            # Wrap text
            text_lines = [incident['summary'][i:i+75] for i in range(0, len(incident['summary']), 75)]
            y = 590
            for line in text_lines:
                c.drawString(60, y, line)
                y -= 15

            c.setFont("Helvetica-Bold", 11)
            c.drawString(60, y-10, "Mitigation Applied:")
            c.setFont("Helvetica", 9)
            mit_lines = [incident['mitigation'][i:i+75] for i in range(0, len(incident['mitigation']), 75)]
            y -= 25
            for line in mit_lines:
                c.drawString(60, y, line)
                y -= 15

            c.showPage()
            c.save()

        except Exception:
            # Fallback text PDF mock file
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"OIL INDIA LIMITED REPORT {filename}\nWell: {incident['well_id']}\nMD: {incident['md']}\nSummary: {incident['summary']}\nMitigation: {incident['mitigation']}\n")
