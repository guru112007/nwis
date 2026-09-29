import React from 'react';
import { Play, Pause, FastForward, RotateCcw, Compass, Gauge, Flame, Droplets } from 'lucide-react';

export default function TelemetryControls({
  telemetry,
  isPaused,
  speed,
  onTogglePause,
  onChangeSpeed,
  onSeekMd
}) {
  const t = telemetry || {
    bit_depth_md_m: 2150.0,
    bit_depth_tvd_m: 2042.5,
    bit_depth_tvdss_m: 1940.0,
    current_formation: 'Tipam Sandstone',
    rop_mhr: 14.5,
    wob_klbs: 22.0,
    torque_kftlbs: 18.0,
    spp_psi: 2450.0,
    flow_in_gpm: 620.0,
    flow_out_gpm: 618.0
  };

  return (
    <div className="bg-[#0B0F19] border-b border-slate-800 px-6 py-2.5 flex flex-wrap items-center justify-between gap-4">
      {/* Telemetry Digital Gauges */}
      <div className="flex items-center space-x-6 overflow-x-auto py-1">

        {/* Active Well */}
        <div className="flex flex-col">
          <span className="text-[10px] uppercase tracking-wider text-slate-400 font-mono">ACTIVE DRILLING RIG</span>
          <span className="text-sm font-bold text-cyan-400 font-mono">NH-24 (Nahorkatiya)</span>
        </div>

        <div className="h-7 w-[1px] bg-slate-800"></div>

        {/* Measured Depth */}
        <div className="flex flex-col">
          <span className="text-[10px] uppercase tracking-wider text-slate-400 font-mono">BIT DEPTH (MD)</span>
          <div className="flex items-baseline space-x-1">
            <span className="text-lg font-bold text-slate-100 font-mono tracking-tight">{t.bit_depth_md_m.toFixed(1)}</span>
            <span className="text-xs text-slate-400 font-mono">m</span>
          </div>
        </div>

        {/* TVD / TVDSS */}
        <div className="flex flex-col">
          <span className="text-[10px] uppercase tracking-wider text-slate-400 font-mono">TVD / TVDSS</span>
          <div className="flex items-baseline space-x-1">
            <span className="text-sm font-semibold text-slate-200 font-mono">{t.bit_depth_tvd_m.toFixed(1)}</span>
            <span className="text-[10px] text-slate-400">/</span>
            <span className="text-sm font-semibold text-cyan-300 font-mono">{t.bit_depth_tvdss_m.toFixed(1)} m</span>
          </div>
        </div>

        <div className="h-7 w-[1px] bg-slate-800"></div>

        {/* Current Formation */}
        <div className="flex flex-col">
          <span className="text-[10px] uppercase tracking-wider text-slate-400 font-mono">CURRENT FORMATION</span>
          <span className="text-xs font-bold text-amber-400 font-mono px-2 py-0.5 bg-amber-950/50 border border-amber-800/60 rounded">
            {t.current_formation}
          </span>
        </div>

        <div className="h-7 w-[1px] bg-slate-800"></div>

        {/* Operational Telemetry Metrics */}
        <div className="flex items-center space-x-4">
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-400 font-mono">ROP</span>
            <span className="text-xs font-bold text-emerald-400 font-mono">{t.rop_mhr} m/hr</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-400 font-mono">WOB</span>
            <span className="text-xs font-bold text-slate-200 font-mono">{t.wob_klbs} klbs</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-400 font-mono">TORQUE</span>
            <span className="text-xs font-bold text-slate-200 font-mono">{t.torque_kftlbs} kft-lb</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-400 font-mono">SPP</span>
            <span className="text-xs font-bold text-blue-400 font-mono">{t.spp_psi} psi</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-400 font-mono">FLOW IN/OUT</span>
            <span className="text-xs font-bold text-slate-200 font-mono">{t.flow_in_gpm}/{t.flow_out_gpm} GPM</span>
          </div>
        </div>

      </div>

      {/* Replay Simulator Controls */}
      <div className="flex items-center space-x-3 bg-slate-900 border border-slate-800 p-1.5 rounded-lg">
        <button
          onClick={onTogglePause}
          className={`p-1.5 rounded-md font-medium text-xs flex items-center space-x-1 transition ${
            isPaused
              ? 'bg-emerald-600 hover:bg-emerald-500 text-white'
              : 'bg-amber-600 hover:bg-amber-500 text-white'
          }`}
        >
          {isPaused ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
          <span>{isPaused ? 'RESUME' : 'PAUSE'}</span>
        </button>

        {/* Speed Multipliers */}
        <div className="flex items-center space-x-1 bg-slate-950 p-0.5 rounded border border-slate-800">
          {[1, 5, 20].map((s) => (
            <button
              key={s}
              onClick={() => onChangeSpeed(s)}
              className={`px-2 py-0.5 text-xs font-mono rounded font-semibold transition ${
                speed === s
                  ? 'bg-cyan-600 text-white'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {s}x
            </button>
          ))}
        </div>

        {/* Depth Scrubber */}
        <div className="flex items-center space-x-2 pl-2">
          <input
            type="range"
            min="1000"
            max="3500"
            step="10"
            value={t.bit_depth_md_m}
            onChange={(e) => onSeekMd(parseFloat(e.target.value))}
            className="w-32 h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
          />
        </div>
      </div>
    </div>
  );
}
