import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.database import engine, Base
from app.api import wells, stratigraphy, alerts, documents, backtest
from app.websockets import telemetry

# Create DB tables if not present
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="eRTMAC-NWIS (Nearby Wells Intelligence System)",
    description="Oil India Limited (SIH PS 26121) Real-Time Offset Well Look-Ahead Intelligence Engine",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(wells.router)
app.include_router(stratigraphy.router)
app.include_router(alerts.router)
app.include_router(documents.router)
app.include_router(backtest.router)
app.include_router(telemetry.router)

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "system": "eRTMAC-NWIS",
        "organization": "Oil India Limited (OIL)",
        "sih_ps": "26121"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
