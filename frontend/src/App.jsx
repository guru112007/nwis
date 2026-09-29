import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import TelemetryControls from './components/TelemetryControls';
import PanelSpatial from './components/PanelSpatial';
import PanelStratigraphy from './components/PanelStratigraphy';
import PanelAlertFeed from './components/PanelAlertFeed';
import PdfViewerModal from './components/PdfViewerModal';
import BacktestView from './components/BacktestView';
import ReviewerQueueModal from './components/ReviewerQueueModal';

import { fetchWells, fetchStratigraphy } from './services/api';

export default function App() {
  const [telemetry, setTelemetry] = useState({
    well_id: "NH-24",
    timestamp: new Date().toISOString(),
    bit_depth_md_m: 2120.0,
    bit_depth_tvd_m: 2014.0,
    bit_depth_tvdss_m: 1911.5,
    current_formation: "Tipam Sandstone",
    rop_mhr: 18.2,
    wob_klbs: 22.5,
    torque_kftlbs: 18.0,
    spp_psi: 2300.0,
    flow_in_gpm: 620.0,
    flow_out_gpm: 605.0
  });

  const [alerts, setAlerts] = useState([]);
  const [isPaused, setIsPaused] = useState(false);
  const [speed, setSpeed] = useState(5);

  const [wells, setWells] = useState([]);
  const [stratigraphy, setStratigraphy] = useState([]);

  // Modals state
  const [activePdfAlert, setActivePdfAlert] = useState(null);
  const [showBacktest, setShowBacktest] = useState(false);
  const [showReviewerQueue, setShowReviewerQueue] = useState(false);

  const wsRef = useRef(null);

  useEffect(() => {
    // Initial data fetch
    fetchWells().then(data => setWells(data)).catch(() => {});
    fetchStratigraphy().then(data => setStratigraphy(data)).catch(() => {});

    // Establish WebSocket Connection for real-time telemetry stream
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/telemetry/NH-24`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.telemetry) {
          setTelemetry(payload.telemetry);
        }
        if (payload.alerts) {
          setAlerts(payload.alerts);
        }
      } catch (err) {
        console.error("WebSocket message parsing error", err);
      }
    };

    return () => {
      if (ws) ws.close();
    };
  }, []);

  const handleTogglePause = () => {
    const nextState = !isPaused;
    setIsPaused(nextState);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ is_paused: nextState }));
    }
  };

  const handleChangeSpeed = (newSpeed) => {
    setSpeed(newSpeed);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ speed: newSpeed }));
    }
  };

  const handleSeekMd = (seekMd) => {
    setTelemetry(prev => ({ ...prev, bit_depth_md_m: seekMd }));
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ seek_md: seekMd }));
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#070A10] text-slate-100">
      {/* Header Bar */}
      <Header
        onOpenBacktest={() => setShowBacktest(true)}
        onOpenReviewerQueue={() => setShowReviewerQueue(true)}
        alertCount={alerts.length}
      />

      {/* Telemetry Readout & Controls */}
      <TelemetryControls
        telemetry={telemetry}
        isPaused={isPaused}
        speed={speed}
        onTogglePause={handleTogglePause}
        onChangeSpeed={handleChangeSpeed}
        onSeekMd={handleSeekMd}
      />

      {/* 3-Panel Control Room Dashboard */}
      <main className="flex-1 p-4 grid grid-cols-1 lg:grid-cols-12 gap-4 overflow-hidden">
        {/* Panel 1: Spatial GIS Map & 3D Clearance */}
        <div className="lg:col-span-4 h-full overflow-hidden">
          <PanelSpatial
            wells={wells}
            activeWellId="NH-24"
            activeMd={telemetry.bit_depth_md_m}
          />
        </div>

        {/* Panel 2: Stratigraphy & Well Log Cross-Section */}
        <div className="lg:col-span-4 h-full overflow-hidden">
          <PanelStratigraphy
            activeMd={telemetry.bit_depth_md_m}
            stratigraphy={stratigraphy}
          />
        </div>

        {/* Panel 3: Look-Ahead Intelligence Feed */}
        <div className="lg:col-span-4 h-full overflow-hidden">
          <PanelAlertFeed
            alerts={alerts}
            activeMd={telemetry.bit_depth_md_m}
            onOpenPdf={(alertObj) => setActivePdfAlert(alertObj)}
          />
        </div>
      </main>

      {/* Modals & Drawers */}
      {activePdfAlert && (
        <PdfViewerModal
          alertData={activePdfAlert}
          onClose={() => setActivePdfAlert(null)}
        />
      )}

      {showBacktest && (
        <BacktestView
          onClose={() => setShowBacktest(false)}
        />
      )}

      {showReviewerQueue && (
        <ReviewerQueueModal
          onClose={() => setShowReviewerQueue(false)}
        />
      )}
    </div>
  );
}
