from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class WellSurveyBase(BaseModel):
    md_m: float = Field(..., alias="md")
    inc_deg: float = Field(..., alias="inc")
    az_deg: float = Field(..., alias="az")
    tvd_m: float = Field(..., alias="tvd")
    tvdss_m: float = Field(..., alias="tvdss")
    dx_north_m: float = Field(..., alias="dx_north")
    dy_east_m: float = Field(..., alias="dy_east")

    class Config:
        populate_by_name = True
        from_attributes = True


class FormationTopBase(BaseModel):
    formation_name: str
    md_top_m: float = Field(..., alias="md_top")
    tvdss_top_m: float = Field(..., alias="tvdss_top")

    class Config:
        populate_by_name = True
        from_attributes = True


class LogCurvePoint(BaseModel):
    md_m: float = Field(..., alias="md")
    gr_api: Optional[float] = Field(None, alias="gr")
    res_ohmm: Optional[float] = Field(None, alias="res")
    dt_usft: Optional[float] = Field(None, alias="dt")

    class Config:
        populate_by_name = True
        from_attributes = True


class OperationalEventSchema(BaseModel):
    id: int
    well_id: str
    md_m: float = Field(..., alias="md")
    tvd_m: float = Field(..., alias="tvd")
    tvdss_m: float = Field(..., alias="tvdss")
    formation: str
    event_category: str
    severity: str
    summary: str
    mitigation: str
    source_file: str
    source_page: int
    bbox: Optional[List[float]] = None
    doc_hash: str
    verified_by_human: bool
    ocr_confidence: float

    class Config:
        populate_by_name = True
        from_attributes = True


class WellSchema(BaseModel):
    id: str
    name: str
    surface_lat: float
    surface_lon: float
    kb_elevation_m: float = Field(..., alias="kb_elevation")
    water_depth_m: float = Field(..., alias="water_depth")
    is_synthetic: bool
    field_name: str
    operator: str

    class Config:
        populate_by_name = True
        from_attributes = True


class TelemetryFrame(BaseModel):
    well_id: str
    timestamp: str
    bit_depth_md_m: float
    bit_depth_tvd_m: float
    bit_depth_tvdss_m: float
    current_formation: str
    rop_mhr: float
    wob_klbs: float
    torque_kftlbs: float
    spp_psi: float
    flow_in_gpm: float
    flow_out_gpm: float


class LookAheadAlert(BaseModel):
    alert_id: str
    tier: str  # L1, L2, L3
    distance_to_event_m: float
    uncertainty_window_m: str
    active_well_id: str
    active_md_m: float
    active_tvdss_m: float
    target_formation: str
    offset_well_id: str
    offset_event_id: int
    event_category: str
    historical_summary: str
    mitigation_applied: str
    playbook_recommendation: str
    heuristic_risk_score: float
    source_file: str
    source_page: int
    bbox: Optional[List[float]] = None
    doc_hash: str
    verified_by_human: bool
    ocr_confidence: float


class AlertFeedbackRequest(BaseModel):
    alert_id: str
    user_action: str  # "USEFUL" or "DISMISSED"
    comments: Optional[str] = None


class BacktestMetrics(BaseModel):
    total_wells_tested: int
    total_incidents_evaluated: int
    hit_rate_pct: float
    median_lead_distance_m: float
    false_alert_rate_per_1000m: float
    l1_alerts_triggered: int
    l2_alerts_triggered: int
    l3_alerts_triggered: int
