import React, { useState } from 'react';
import { ShieldAlert, AlertTriangle, Info, FileText, CheckCircle2, XCircle, ChevronRight, ExternalLink } from 'lucide-react';
import { sendAlertFeedback } from '../services/api';

export default function PanelAlertFeed({ alerts = [], activeMd = 2150.0, onOpenPdf }) {
  const [feedbackState, setFeedbackState] = useState({});

  const handleFeedback = async (alertId, action) => {
    try {
      await sendAlertFeedback(alertId, action);
      setFeedbackState(prev => ({ ...prev, [alertId]: action }));
    } catch (err) {
      console.error("Failed to send feedback", err);
    }
  };

  const getTierBadge = (tier) => {
    switch (tier) {
      case 'L3':
        return {
          bg: 'bg-rose-950/80 border-rose-600 text-rose-300',
          badgeBg: 'bg-rose-600 text-white',
          label: 'L3 CRITICAL (0 - 15m)',
          icon: ShieldAlert
        };
      case 'L2':
        return {
          bg: 'bg-amber-950/80 border-amber-600 text-amber-300',
          badgeBg: 'bg-amber-500 text-slate-950 font-bold',
          label: 'L2 CORRIDOR WARNING (15 - 50m)',
          icon: AlertTriangle
        };
      case 'L1':
      default:
        return {
          bg: 'bg-cyan-950/80 border-cyan-700 text-cyan-300',
          badgeBg: 'bg-cyan-600 text-white',
          label: 'L1 ADVISORY (50 - 100m)',
          icon: Info
        };
    }
  };

  return (
    <div className="bg-[#0B0F19] border border-slate-800 rounded-xl p-4 flex flex-col h-full shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-2">
        <div className="flex items-center space-x-2">
          <ShieldAlert className="w-5 h-5 text-rose-400" />
          <h2 className="text-sm font-semibold text-slate-100 uppercase tracking-wider font-mono">
            Panel 3: Look-Ahead Intelligence Feed
          </h2>
        </div>
        <span className="text-xs font-mono font-bold text-rose-400 bg-rose-950/60 border border-rose-800 px-2 py-0.5 rounded">
          {alerts.length} ACTIVE ALERTS
        </span>
      </div>

      {/* Alert Feed Scroll Container */}
      <div className="flex-1 overflow-y-auto space-y-3.5 pr-1">
        {alerts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-slate-500 text-center p-4">
            <CheckCircle2 className="w-10 h-10 text-emerald-500 mb-2 opacity-80" />
            <p className="text-sm font-medium text-slate-300">No Offset Hazards in Immediate Horizon</p>
            <p className="text-xs text-slate-500 mt-1">
              Active bit depth ({activeMd.toFixed(1)}m MD) is clear of offset incidents.
            </p>
          </div>
        ) : (
          alerts.map((a, idx) => {
            const config = getTierBadge(a.tier);
            const IconComp = config.icon;
            const actionTaken = feedbackState[a.alert_id];

            return (
              <div
                key={a.alert_id || idx}
                className={`border rounded-xl p-4 transition shadow-md backdrop-blur-sm ${config.bg}`}
              >
                {/* Alert Top Row */}
                <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5 mb-2.5">
                  <div className="flex items-center space-x-2">
                    <span className={`px-2.5 py-0.5 text-[11px] font-mono font-bold rounded ${config.badgeBg}`}>
                      {config.label}
                    </span>
                    <span className="text-xs font-mono font-semibold text-slate-300">
                      {a.event_category}
                    </span>
                  </div>

                  {/* Heuristic Risk Score */}
                  <div className="flex items-center space-x-1.5 bg-slate-900 border border-slate-800 px-2.5 py-1 rounded-md">
                    <span className="text-[10px] font-mono text-slate-400">RISK SCORE:</span>
                    <span className="text-xs font-mono font-bold text-rose-400">{a.heuristic_risk_score} / 100</span>
                  </div>
                </div>

                {/* Depth & Uncertainty Window */}
                <div className="grid grid-cols-2 gap-2 text-xs font-mono mb-3 bg-slate-900/90 p-2.5 rounded-lg border border-slate-800">
                  <div>
                    <span className="text-slate-400">Distance Ahead:</span>{' '}
                    <span className="font-bold text-slate-100">{a.distance_to_event_m} m</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Target Formation:</span>{' '}
                    <span className="font-bold text-amber-400">{a.target_formation}</span>
                  </div>
                  <div className="col-span-2 text-[11px] text-slate-300">
                    <span className="text-slate-400">Uncertainty Window:</span> {a.uncertainty_window_m}
                  </div>
                </div>

                {/* Lesson & Applied Mitigation */}
                <div className="space-y-2 text-xs text-slate-200 mb-3">
                  <div>
                    <span className="font-bold text-cyan-300 uppercase text-[10px] tracking-wider block font-mono">
                      Historical Offset Incident ({a.offset_well_id}):
                    </span>
                    <p className="mt-0.5 text-slate-300 leading-relaxed">{a.historical_summary}</p>
                  </div>

                  <div className="bg-emerald-950/40 border border-emerald-800/50 p-2.5 rounded-lg">
                    <span className="font-bold text-emerald-400 uppercase text-[10px] tracking-wider block font-mono">
                      Recommended Mitigation Playbook:
                    </span>
                    <p className="mt-0.5 text-emerald-200 font-medium leading-relaxed">
                      {a.playbook_recommendation}
                    </p>
                  </div>
                </div>

                {/* Extractive PDF Citation & Feedback Actions */}
                <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-800/80">
                  {/* Deep-Linked PDF Citation */}
                  <button
                    onClick={() => onOpenPdf(a)}
                    className="flex items-center space-x-1.5 bg-slate-900 hover:bg-slate-800 text-cyan-300 text-xs px-3 py-1.5 rounded-md border border-slate-700 transition"
                  >
                    <FileText className="w-3.5 h-3.5 text-cyan-400" />
                    <span className="font-mono text-[11px]">
                      Citation: {a.source_file} (Page {a.source_page})
                    </span>
                    <ExternalLink className="w-3 h-3 text-cyan-400 ml-1" />
                  </button>

                  {/* Useful / Dismiss Feedback */}
                  <div className="flex items-center space-x-1.5">
                    {actionTaken ? (
                      <span className="text-[11px] font-mono text-emerald-400 font-semibold bg-emerald-950 px-2 py-1 rounded border border-emerald-800">
                        Feedback Recorded: {actionTaken}
                      </span>
                    ) : (
                      <>
                        <button
                          onClick={() => handleFeedback(a.alert_id, 'USEFUL')}
                          className="flex items-center space-x-1 bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-700 text-xs px-2.5 py-1 rounded transition"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Useful</span>
                        </button>
                        <button
                          onClick={() => handleFeedback(a.alert_id, 'DISMISSED')}
                          className="flex items-center space-x-1 bg-slate-800 hover:bg-slate-700 text-slate-400 border border-slate-700 text-xs px-2.5 py-1 rounded transition"
                        >
                          <XCircle className="w-3.5 h-3.5" />
                          <span>Dismiss</span>
                        </button>
                      </>
                    )}
                  </div>
                </div>

              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
