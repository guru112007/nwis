import asyncio
import json
import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Well, WellSurvey, OperationalEvent
from app.engine.mcm import MinimumCurvatureMethod
from app.engine.alert_engine import LookAheadAlertEngine
from app.config import STRATIGRAPHY_CONFIG

router = APIRouter()

class TelemetryReplaySimulator:
    def __init__(self, well_id: str = "NH-24"):
        self.well_id = well_id
        self.current_md = 1500.0  # Start depth (m)
        self.max_md = 3500.0
        self.rop_mhr = 12.5       # Rate of Penetration (m/hr)
        self.wob_klbs = 24.0
        self.torque_kftlbs = 18.5
        self.spp_psi = 2450.0
        self.flow_in_gpm = 620.0
        self.flow_out_gpm = 618.0
        self.speed_multiplier = 5.0
        self.is_paused = False

    def get_current_formation(self, md: float) -> str:
        for fmt in STRATIGRAPHY_CONFIG.get("stratigraphy", []):
            if fmt["top_md_m"] <= md <= fmt["base_md_m"]:
                return fmt["name"]
        return "Kopili Shale"

    def step(self) -> Dict[str, Any]:
        if not self.is_paused:
            # Advance depth by 1m * speed_multiplier factor per tick
            advance_step = 0.5 * (self.speed_multiplier / 5.0)
            self.current_md += advance_step
            if self.current_md > self.max_md:
                self.current_md = 1500.0  # Loop replay for continuous hero demo

        # Determine current formation
        formation = self.get_current_formation(self.current_md)

        # Approximate TVD/TVDSS for telemetry frame
        tvd = self.current_md * 0.95
        tvdss = tvd - 102.5

        # Telemetry perturbations based on formation
        if formation == "Tipam Sandstone":
            rop = 18.2
            spp = 2300.0
            flow_out = 605.0 # Partial mud loss
        elif formation == "Barail Sand/Coal":
            rop = 8.5
            spp = 2650.0
            flow_out = 622.0
        elif formation == "Kopili Shale":
            rop = 6.0
            spp = 2780.0
            flow_out = 619.0
        else:
            rop = 14.0
            spp = 2450.0
            flow_out = 620.0

        return {
            "well_id": self.well_id,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "bit_depth_md_m": round(self.current_md, 1),
            "bit_depth_tvd_m": round(tvd, 1),
            "bit_depth_tvdss_m": round(tvdss, 1),
            "current_formation": formation,
            "rop_mhr": round(rop, 1),
            "wob_klbs": round(self.wob_klbs, 1),
            "torque_kftlbs": round(self.torque_kftlbs, 1),
            "spp_psi": round(spp, 1),
            "flow_in_gpm": round(self.flow_in_gpm, 1),
            "flow_out_gpm": round(flow_out, 1)
        }

@router.websocket("/ws/telemetry/{well_id}")
async def websocket_telemetry_endpoint(websocket: WebSocket, well_id: str):
    await websocket.accept()
    simulator = TelemetryReplaySimulator(well_id=well_id)
    alert_engine = LookAheadAlertEngine()

    db: Session = SessionLocal()
    try:
        active_well_obj = db.query(Well).filter(Well.id == well_id).first()
        active_well_dict = {
            "id": active_well_obj.id if active_well_obj else well_id,
            "surface_lat": active_well_obj.surface_lat if active_well_obj else 27.4850,
            "surface_lon": active_well_obj.surface_lon if active_well_obj else 95.3400
        }

        offset_wells_objs = db.query(Well).filter(Well.id != well_id).all()
        offset_wells = [
            {"id": w.id, "surface_lat": w.surface_lat, "surface_lon": w.surface_lon}
            for w in offset_wells_objs
        ]

        offset_events_objs = db.query(OperationalEvent).all()
        offset_events = [
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
            for e in offset_events_objs
        ]
    finally:
        db.close()

    try:
        while True:
            # Handle incoming control messages (e.g. speed multiplier, pause/play, seek)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.01)
                msg = json.loads(data)
                if "speed" in msg:
                    simulator.speed_multiplier = float(msg["speed"])
                if "is_paused" in msg:
                    simulator.is_paused = bool(msg["is_paused"])
                if "seek_md" in msg:
                    simulator.current_md = float(msg["seek_md"])
            except asyncio.TimeoutError:
                pass
            except Exception:
                pass

            frame = simulator.step()

            # Compute real-time 3-tier look-ahead alerts
            alerts = alert_engine.evaluate_active_bit(
                active_well=active_well_dict,
                active_bit_md=frame["bit_depth_md_m"],
                active_bit_tvdss=frame["bit_depth_tvdss_m"],
                current_formation=frame["current_formation"],
                offset_wells=offset_wells,
                offset_events=offset_events
            )

            payload = {
                "telemetry": frame,
                "alerts": alerts,
                "is_paused": simulator.is_paused,
                "speed": simulator.speed_multiplier
            }

            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(0.4) # 2.5 FPS update rate

    except WebSocketDisconnect:
        print(f"WebSocket client disconnected from telemetry stream {well_id}")
