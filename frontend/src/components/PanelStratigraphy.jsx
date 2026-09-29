import React from 'react';
import { Layers, TrendingUp, AlertTriangle } from 'lucide-react';

export default function PanelStratigraphy({ activeMd = 2150.0, stratigraphy = [] }) {
  // Default Upper Assam stratigraphy sequence if not loaded
  const defaultStrat = stratigraphy.length > 0 ? stratigraphy : [
    { name: "Alluvium", top_md_m: 0, base_md_m: 250, color: "#94A3B8", typical_gr_api: 35 },
    { name: "Dhekiajuli", top_md_m: 250, base_md_m: 800, color: "#38BDF8", typical_gr_api: 50 },
    { name: "Girujan Clay", top_md_m: 800, base_md_m: 1650, color: "#A855F7", typical_gr_api: 85 },
    { name: "Tipam Sandstone", top_md_m: 1650, base_md_m: 2500, color: "#F59E0B", typical_gr_api: 40 },
    { name: "Barail Sand/Coal", top_md_m: 2500, base_md_m: 3200, color: "#EF4444", typical_gr_api: 95 },
    { name: "Kopili Shale", top_md_m: 3200, base_md_m: 3800, color: "#6366F1", typical_gr_api: 120 }
  ];

  const maxDepth = 3500;
  const svgHeight = 520;
  const bitY = (activeMd / maxDepth) * svgHeight;

  // Generate synthetic GR curve SVG path points
  const grPoints = [];
  for (let md = 0; md <= maxDepth; md += 40) {
    const y = (md / maxDepth) * svgHeight;
    let baseGr = 45;
    if (md > 800 && md <= 1650) baseGr = 85;
    if (md > 1650 && md <= 2500) baseGr = 40;
    if (md > 2500 && md <= 3200) baseGr = 95;
    if (md > 3200) baseGr = 125;

    const grVal = baseGr + Math.sin(md * 0.05) * 15;
    const x = 20 + (grVal / 150) * 100; // Map GR 0-150 to X pixel 20-120
    grPoints.push(`${x},${y}`);
  }

  // Offset incidents depth flags
  const incidents = [
    { md: 1980, label: "BGB-12 Mud Loss (1980m)", color: "#F59E0B" },
    { md: 2150, label: "NH-02 Severe Loss (2150m)", color: "#F59E0B" },
    { md: 2780, label: "NH-09 Stuck Pipe (2780m)", color: "#EF4444" },
    { md: 2920, label: "JLN-04 Gas Kick (2920m)", color: "#EF4444" },
    { md: 3410, label: "NH-15 Sloughing Shale (3410m)", color: "#A855F7" }
  ];

  return (
    <div className="bg-[#0B0F19] border border-slate-800 rounded-xl p-4 flex flex-col h-full shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-2">
        <div className="flex items-center space-x-2">
          <Layers className="w-5 h-5 text-amber-400" />
          <h2 className="text-sm font-semibold text-slate-100 uppercase tracking-wider font-mono">
            Panel 2: Stratigraphy & Cross-Section Logs
          </h2>
        </div>
        <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 border border-cyan-800 px-2 py-0.5 rounded">
          TVDSS Aligned (-102.5m KB)
        </span>
      </div>

      {/* Multi-Track SVG Viewer */}
      <div className="relative flex-1 w-full bg-[#070A10] rounded-lg overflow-y-auto overflow-x-hidden border border-slate-800 p-2">

        {/* Track Headers */}
        <div className="grid grid-cols-12 gap-1 text-[10px] font-mono font-bold text-slate-400 border-b border-slate-800 pb-1 mb-1 text-center">
          <div className="col-span-4 text-emerald-400">TRACK 1: GR LOG (API 0-150)</div>
          <div className="col-span-4 text-amber-400">TRACK 2: ASSAM STRATIGRAPHY</div>
          <div className="col-span-4 text-rose-400">TRACK 3: INCIDENT HORIZONS</div>
        </div>

        <svg width="100%" height={svgHeight} className="overflow-visible">
          {/* Stratigraphy Formations Background Bands (Track 2) */}
          {defaultStrat.map((fmt, idx) => {
            const yTop = (fmt.top_md_m / maxDepth) * svgHeight;
            const yBase = (fmt.base_md_m / maxDepth) * svgHeight;
            const height = yBase - yTop;

            return (
              <g key={idx}>
                {/* Stratigraphy Rect */}
                <rect
                  x="33%"
                  y={yTop}
                  width="33%"
                  height={height}
                  fill={fmt.color || '#334155'}
                  fillOpacity="0.2"
                  stroke="#1E293B"
                  strokeWidth="1"
                />
                {/* Formation Top Line & Label */}
                <line x1="0" y1={yTop} x2="100%" y2={yTop} stroke="#334155" strokeWidth="1" strokeDasharray="2,2" />
                <text x="35%" y={yTop + 14} fill="#F1F5F9" fontSize="10" fontFamily="JetBrains Mono" fontWeight="bold">
                  {fmt.name} ({fmt.top_md_m}m)
                </text>
              </g>
            );
          })}

          {/* Track 1: Gamma Ray Curve */}
          <polyline
            fill="none"
            stroke="#10B981"
            strokeWidth="2"
            points={grPoints.join(" ")}
          />

          {/* Track 3: Historical Offset Incident Depth Markers */}
          {incidents.map((inc, i) => {
            const incY = (inc.md / maxDepth) * svgHeight;
            return (
              <g key={i}>
                <line x1="67%" y1={incY} x2="100%" y2={incY} stroke={inc.color} strokeWidth="1.5" strokeDasharray="3,3" />
                <rect x="68%" y={incY - 9} width="30%" height="16" rx="3" fill="#1E293B" stroke={inc.color} strokeWidth="1" />
                <text x="70%" y={incY + 3} fill={inc.color} fontSize="9" fontFamily="JetBrains Mono" fontWeight="bold">
                  {inc.label}
                </text>
              </g>
            );
          })}

          {/* Animated Active Bit Position Line */}
          <g>
            <line x1="0" y1={bitY} x2="100%" y2={bitY} stroke="#EF4444" strokeWidth="2.5" />
            <polygon points={`0,${bitY-5} 10,${bitY} 0,${bitY+5}`} fill="#EF4444" />
            <rect x="5" y={bitY - 10} width="95" height="18" rx="4" fill="#EF4444" />
            <text x="10" y={bitY + 3} fill="#FFFFFF" fontSize="10" fontFamily="JetBrains Mono" fontWeight="bold">
              BIT: {activeMd.toFixed(1)}m MD
            </text>
          </g>
        </svg>

      </div>
    </div>
  );
}
