import datetime
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Well(Base):
    __tablename__ = "wells"

    id = Column(String, primary_key=True, index=True) # e.g. 'NH-24'
    name = Column(String, nullable=False)
    surface_lat = Column(Float, nullable=False)
    surface_lon = Column(Float, nullable=False)
    kb_elevation = Column(Float, nullable=False, default=102.5) # KB elevation in meters above MSL
    water_depth = Column(Float, nullable=False, default=0.0)    # Water depth (0.0 for onshore Assam)
    is_synthetic = Column(Boolean, nullable=False, default=True)
    field_name = Column(String, nullable=False, default="Nahorkatiya")
    operator = Column(String, nullable=False, default="Oil India Limited (OIL)")

    surveys = relationship("WellSurvey", back_populates="well", cascade="all, delete-orphan")
    formation_tops = relationship("FormationTop", back_populates="well", cascade="all, delete-orphan")
    log_curves = relationship("LogCurve", back_populates="well", cascade="all, delete-orphan")
    operational_events = relationship("OperationalEvent", back_populates="well", cascade="all, delete-orphan")


class WellSurvey(Base):
    __tablename__ = "well_surveys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    well_id = Column(String, ForeignKey("wells.id"), nullable=False, index=True)
    md = Column(Float, nullable=False)        # Measured Depth (m)
    inc = Column(Float, nullable=False)       # Inclination (degrees)
    az = Column(Float, nullable=False)        # Azimuth (degrees)
    tvd = Column(Float, nullable=False)       # True Vertical Depth (m)
    tvdss = Column(Float, nullable=False)     # True Vertical Depth Subsea (m)
    dx_north = Column(Float, nullable=False)  # Displacement North (m)
    dy_east = Column(Float, nullable=False)   # Displacement East (m)

    well = relationship("Well", back_populates="surveys")


class FormationTop(Base):
    __tablename__ = "formation_tops"

    id = Column(Integer, primary_key=True, autoincrement=True)
    well_id = Column(String, ForeignKey("wells.id"), nullable=False, index=True)
    formation_name = Column(String, nullable=False)
    md_top = Column(Float, nullable=False)
    tvdss_top = Column(Float, nullable=False)

    well = relationship("Well", back_populates="formation_tops")


class LogCurve(Base):
    __tablename__ = "log_curves"

    id = Column(Integer, primary_key=True, autoincrement=True)
    well_id = Column(String, ForeignKey("wells.id"), nullable=False, index=True)
    md = Column(Float, nullable=False, index=True)
    gr = Column(Float, nullable=True)   # Gamma Ray (API)
    res = Column(Float, nullable=True)  # Resistivity (ohm-m)
    dt = Column(Float, nullable=True)   # Delta-T Sonic (us/ft)

    well = relationship("Well", back_populates="log_curves")


class OperationalEvent(Base):
    __tablename__ = "operational_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    well_id = Column(String, ForeignKey("wells.id"), nullable=False, index=True)
    md = Column(Float, nullable=False)
    tvd = Column(Float, nullable=False)
    tvdss = Column(Float, nullable=False)
    formation = Column(String, nullable=False)
    event_category = Column(String, nullable=False) # e.g. "Severe Mud Loss", "Differential Pipe Sticking"
    severity = Column(String, nullable=False)       # "L1", "L2", "L3"
    summary = Column(Text, nullable=False)
    mitigation = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)         # 384-dimensional vector list
    source_file = Column(String, nullable=False)
    source_page = Column(Integer, nullable=False)
    bbox = Column(JSON, nullable=True)              # [x0, y0, x1, y1] normalized bounding box
    doc_hash = Column(String, nullable=False)
    verified_by_human = Column(Boolean, nullable=False, default=True)
    ocr_confidence = Column(Float, nullable=False, default=0.98)

    well = relationship("Well", back_populates="operational_events")


class AlertFeedback(Base):
    __tablename__ = "alert_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(String, nullable=False, index=True)
    user_action = Column(String, nullable=False) # "USEFUL" or "DISMISSED"
    comments = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
