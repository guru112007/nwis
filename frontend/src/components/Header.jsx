import React from 'react';
import { ShieldCheck, Database, PlayCircle, Layers, FileCheck, Activity } from 'lucide-react';

export default function Header({ onOpenBacktest, onOpenReviewerQueue, alertCount = 0 }) {
  return (
    <header className="bg-[#0B0F19] border-b border-slate-800 px-6 py-3 flex items-center justify-between shadow-lg">
      {/* Left Branding */}
      <div className="flex items-center space-x-4">
        <div className="bg-gradient-to-r from-cyan-600 to-blue-700 text-white p-2 rounded-lg font-bold text-lg tracking-wider flex items-center space-x-2">
          <Activity className="w-6 h-6 text-cyan-300 animate-pulse" />
          <span>eRTMAC-NWIS</span>
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-sm font-semibold text-slate-100 tracking-wide">
              Nearby Wells Intelligence System
            </h1>
            <span className="bg-blue-950 text-cyan-400 border border-cyan-800/60 text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold">
              SIH PS 26121 | OIL INDIA LIMITED
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Real-Time Look-Ahead Offset Well Risk Mitigation & Extractive QA
          </p>
        </div>
      </div>

      {/* Middle Synthetic Data Badge */}
      <div className="hidden md:flex items-center space-x-2 bg-amber-950/40 border border-amber-600/40 px-3 py-1 rounded-md">
        <Database className="w-4 h-4 text-amber-400" />
        <span className="text-xs text-amber-300 font-mono font-medium">
          DATASET: Upper Assam Shelf <span className="bg-amber-500 text-slate-950 font-bold px-1 py-0.5 rounded text-[10px]">is_synthetic = true</span>
        </span>
      </div>

      {/* Right Actions */}
      <div className="flex items-center space-x-3">
        <button
          onClick={onOpenReviewerQueue}
          className="flex items-center space-x-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-3 py-1.5 rounded-md border border-slate-700 transition"
        >
          <FileCheck className="w-4 h-4 text-amber-400" />
          <span>OCR Review Queue</span>
        </button>

        <button
          onClick={onOpenBacktest}
          className="flex items-center space-x-1.5 bg-cyan-950 hover:bg-cyan-900 border border-cyan-700 text-cyan-300 text-xs px-3.5 py-1.5 rounded-md font-medium transition shadow-sm"
        >
          <PlayCircle className="w-4 h-4 text-cyan-400" />
          <span>Backtest Harness</span>
        </button>

        <div className="flex items-center space-x-1 text-xs text-emerald-400 bg-emerald-950/60 border border-emerald-800/50 px-2.5 py-1 rounded-md font-mono">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          <span>SYSTEM ONLINE</span>
        </div>
      </div>
    </header>
  );
}
