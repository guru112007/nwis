import React, { useState, useEffect, useRef } from 'react';
import { Layers, MapPin, Eye, Box, Compass } from 'lucide-react';

export default function PanelSpatial({ wells = [], activeWellId = "NH-24", activeMd = 2150.0 }) {
  const [viewMode, setViewMode] = useState('2D'); // '2D' or '3D'
  const canvasRef = useRef(null);

  // Default Upper Assam field wells if not loaded yet
  const defaultWells = wells.length > 0 ? wells : [
    { id: "NH-24", name: "NH-24 (Active)", surface_lat: 27.4850, surface_lon: 95.3400, is_synthetic: true },
    { id: "NH-02", name: "NH-02", surface_lat: 27.4880, surface_lon: 95.3420, is_synthetic: true },
    { id: "NH-09", name: "NH-09", surface_lat: 27.4810, surface_lon: 95.3370, is_synthetic: true },
    { id: "NH-15", name: "NH-15", surface_lat: 27.4910, surface_lon: 95.3460, is_synthetic: true },
    { id: "JLN-04", name: "JLN-04", surface_lat: 27.4750, surface_lon: 95.3300, is_synthetic: true },
    { id: "BGB-12", name: "BGB-12", surface_lat: 27.4650, surface_lon: 95.3200, is_synthetic: true }
  ];

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = canvas.width = canvas.parentElement.clientWidth;
    const height = canvas.height = canvas.parentElement.clientHeight;

    ctx.clearRect(0, 0, width, height);

    if (viewMode === '2D') {
      // Draw 2D Surface Map (MapLibre style dark GIS viewer)
      ctx.fillStyle = "#0B0F19";
      ctx.fillRect(0, 0, width, height);

      // Grid background lines
      ctx.strokeStyle = "#1E293B";
      ctx.lineWidth = 1;
      const gridSize = 40;
      for (let x = 0; x < width; x += gridSize) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, height); ctx.stroke();
      }
      for (let y = 0; y < height; y += gridSize) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(width, y); ctx.stroke();
      }

      // Center reference point (Nahorkatiya field center)
      const refLat = 27.4850;
      const refLon = 95.3400;
      const scale = 8000.0; // Pixels per degree

      const centerX = width / 2;
      const centerY = height / 2;

      // Draw PostGIS ST_DWithin 5km Surface Radius Circle around NH-24
      ctx.strokeStyle = "rgba(14, 165, 233, 0.4)";
      ctx.fillStyle = "rgba(14, 165, 233, 0.05)";
      ctx.lineWidth = 2;
      ctx.setLineDash([6, 6]);
      ctx.beginPath();
      ctx.arc(centerX, centerY, 180, 0, 2 * Math.PI);
      ctx.fill();
      ctx.stroke();
      ctx.setLineDash([]);

      // Label PostGIS radius
      ctx.fillStyle = "#0EA5E9";
      ctx.font = "10px JetBrains Mono";
      ctx.fillText("PostGIS ST_DWithin Surface Radius (5 km)", centerX - 120, centerY - 190);

      // Draw Wellhead Markers
      defaultWells.forEach(w => {
        const dx = (w.surface_lon - refLon) * scale;
        const dy = -(w.surface_lat - refLat) * scale;
        const px = centerX + dx;
        const py = centerY + dy;

        const isActive = w.id === activeWellId;

        // Draw distance vector line from active well to offset
        if (!isActive) {
          ctx.strokeStyle = "rgba(100, 116, 139, 0.3)";
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(centerX, centerY);
          ctx.lineTo(px, py);
          ctx.stroke();
        }

        // Wellhead Icon
        ctx.beginPath();
        ctx.arc(px, py, isActive ? 9 : 6, 0, 2 * Math.PI);
        ctx.fillStyle = isActive ? "#0EA5E9" : "#64748B";
        ctx.fill();
        ctx.strokeStyle = isActive ? "#FFFFFF" : "#334155";
        ctx.lineWidth = 2;
        ctx.stroke();

        if (isActive) {
          // Pulsing halo for active well NH-24
          ctx.beginPath();
          ctx.arc(px, py, 18, 0, 2 * Math.PI);
          ctx.strokeStyle = "rgba(14, 165, 233, 0.5)";
          ctx.lineWidth = 2;
          ctx.stroke();
        }

        // Well label
        ctx.fillStyle = isActive ? "#38BDF8" : "#94A3B8";
        ctx.font = isActive ? "bold 12px Inter" : "11px Inter";
        ctx.fillText(w.id, px + 12, py + 4);
      });

    } else {
      // Draw 3D Downhole Wellbore Trajectory Viewer
      ctx.fillStyle = "#070A10";
      ctx.fillRect(0, 0, width, height);

      // Draw 3D axis guides
      ctx.strokeStyle = "#334155";
      ctx.lineWidth = 1;
      const startX = width / 2;
      const startY = 40;

      // Surface plane line
      ctx.beginPath(); ctx.moveTo(40, startY); ctx.lineTo(width - 40, startY); ctx.stroke();
      ctx.fillStyle = "#64748B";
      ctx.font = "11px JetBrains Mono";
      ctx.fillText("SURFACE DATUM (KB Elevation 102.5m)", 50, startY - 10);

      // 3D Depth axis down to 3,500m
      ctx.beginPath(); ctx.moveTo(startX, startY); ctx.lineTo(startX, height - 30); ctx.stroke();

      // Render Active Well Trajectory (NH-24)
      const maxDepthPix = height - 80;
      const bitY = startY + (activeMd / 3500.0) * maxDepthPix;

      // Active path curve
      ctx.strokeStyle = "#0EA5E9";
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.moveTo(startX, startY);
      ctx.quadraticCurveTo(startX + 60, startY + (bitY - startY) * 0.5, startX + 80, bitY);
      ctx.stroke();

      // Active Bit Marker
      ctx.beginPath();
      ctx.arc(startX + 80, bitY, 8, 0, 2 * Math.PI);
      ctx.fillStyle = "#EF4444";
      ctx.fill();
      ctx.strokeStyle = "#FFFFFF";
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.fillStyle = "#F87171";
      ctx.font = "bold 11px JetBrains Mono";
      ctx.fillText(`BIT: ${activeMd.toFixed(1)} m MD`, startX + 95, bitY + 4);

      // Draw Offset Trajectories & Incident Horizons
      const offsetPaths = [
        { id: "NH-02", xOffset: -90, incidentMd: 2150, color: "#F59E0B", type: "Mud Loss" },
        { id: "NH-09", xOffset: -160, incidentMd: 2780, color: "#EF4444", type: "Stuck Pipe" },
        { id: "NH-15", xOffset: 140, incidentMd: 3410, color: "#F59E0B", type: "Sloughing Shale" },
        { id: "JLN-04", xOffset: -220, incidentMd: 2920, color: "#EF4444", type: "Gas Kick" }
      ];

      offsetPaths.forEach(op => {
        const offY = startY + maxDepthPix;
        const incY = startY + (op.incidentMd / 3500.0) * maxDepthPix;

        ctx.strokeStyle = "rgba(100, 116, 139, 0.6)";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(startX + op.xOffset, offY);
        ctx.stroke();

        // Incident marker point
        ctx.beginPath();
        ctx.arc(startX + op.xOffset * (op.incidentMd / 3500.0), incY, 6, 0, 2 * Math.PI);
        ctx.fillStyle = op.color;
        ctx.fill();

        ctx.fillStyle = "#CBD5E1";
        ctx.font = "10px Inter";
        ctx.fillText(`${op.id}: ${op.type} (${op.incidentMd}m)`, startX + op.xOffset * (op.incidentMd / 3500.0) + 10, incY);
      });
    }
  }, [viewMode, wells, activeWellId, activeMd]);

  return (
    <div className="bg-[#0B0F19] border border-slate-800 rounded-xl p-4 flex flex-col h-full shadow-lg">
      {/* Header Controls */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-2">
        <div className="flex items-center space-x-2">
          <Compass className="w-5 h-5 text-cyan-400" />
          <h2 className="text-sm font-semibold text-slate-100 uppercase tracking-wider font-mono">
            Panel 1: Spatial GIS & 3D Clearance
          </h2>
        </div>

        {/* 2D / 3D Toggle */}
        <div className="flex items-center space-x-1 bg-slate-900 border border-slate-800 p-0.5 rounded-lg">
          <button
            onClick={() => setViewMode('2D')}
            className={`flex items-center space-x-1 px-3 py-1 rounded text-xs font-semibold transition ${
              viewMode === '2D' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>2D Surface GIS</span>
          </button>
          <button
            onClick={() => setViewMode('3D')}
            className={`flex items-center space-x-1 px-3 py-1 rounded text-xs font-semibold transition ${
              viewMode === '3D' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Box className="w-3.5 h-3.5" />
            <span>3D Wellbores</span>
          </button>
        </div>
      </div>

      {/* Canvas Viewport */}
      <div className="relative flex-1 w-full min-h-[360px] bg-[#070A10] rounded-lg overflow-hidden border border-slate-800/80">
        <canvas ref={canvasRef} className="w-full h-full block" />

        {/* Canvas Legend Overlay */}
        <div className="absolute bottom-3 left-3 bg-slate-900/90 border border-slate-800 p-2.5 rounded-md text-[11px] font-mono text-slate-300 space-y-1 backdrop-blur-sm shadow">
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 inline-block"></span>
            <span>Active Well NH-24 (Bit Depth: {activeMd.toFixed(1)}m)</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block"></span>
            <span>Offset Wells (2D Surface Radius / 3D MCM)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
