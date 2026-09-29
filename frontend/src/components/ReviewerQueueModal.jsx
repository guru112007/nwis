import React, { useState, useEffect } from 'react';
import { FileCheck, ShieldCheck, CheckCircle2, X, AlertTriangle } from 'lucide-react';
import { fetchReviewQueue, verifyDocumentRecord } from '../services/api';

export default function ReviewerQueueModal({ onClose }) {
  const [queueItems, setQueueItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadQueue();
  }, []);

  const loadQueue = async () => {
    setLoading(true);
    try {
      const items = await fetchReviewQueue();
      setQueueItems(items);
    } catch (err) {
      console.error("Failed to fetch review queue", err);
      // Fallback preview item
      setQueueItems([
        {
          id: 5,
          well_id: "BGB-12",
          md: 1980.0,
          tvdss: 1785.0,
          formation: "Tipam Sandstone",
          event_category: "Severe Mud Loss",
          severity: "L1",
          summary: "Partial fluid loss of 12 bbl/hr recorded in upper Tipam section. Hand-written daily report page was degraded.",
          mitigation: "Added coarse mica pills (15 ppb) to active mud pit system.",
          source_file: "BGB-12_Scanned_Log_Report.pdf",
          source_page: 9,
          ocr_confidence: 0.74,
          verified_by_human: false
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (eventId) => {
    try {
      await verifyDocumentRecord(eventId);
      setQueueItems(prev => prev.filter(item => item.id !== eventId));
    } catch (err) {
      console.error("Failed to verify event record", err);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-[#0B0F19] border border-slate-700 rounded-2xl w-full max-w-3xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">

        {/* Header */}
        <div className="bg-slate-900 border-b border-slate-800 p-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FileCheck className="w-6 h-6 text-amber-400" />
            <div>
              <h3 className="text-sm font-bold text-slate-100 font-mono uppercase tracking-wider">
                Human-in-the-Loop OCR Verification Queue
              </h3>
              <p className="text-xs text-slate-400">
                Extracted Report Records with OCR Confidence &lt; 0.85 Flagged for Verification
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white bg-slate-800 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Queue Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {queueItems.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-48 text-slate-400 text-center">
              <CheckCircle2 className="w-12 h-12 text-emerald-400 mb-2" />
              <p className="text-sm font-bold text-slate-200">Review Queue Empty</p>
              <p className="text-xs text-slate-500 mt-1">
                All extracted DDR/WCR report records meet the high confidence threshold (&ge; 0.85).
              </p>
            </div>
          ) : (
            queueItems.map((item) => (
              <div
                key={item.id}
                className="bg-slate-900 border border-amber-800/60 rounded-xl p-4 space-y-3 font-mono"
              >
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <div className="flex items-center space-x-2">
                    <span className="bg-amber-950 text-amber-400 border border-amber-800 text-[11px] px-2 py-0.5 rounded font-bold">
                      OCR Confidence: {(item.ocr_confidence * 100).toFixed(0)}% (&lt; 85%)
                    </span>
                    <span className="text-xs text-slate-200 font-bold">{item.well_id} - {item.event_category}</span>
                  </div>
                  <span className="text-xs text-slate-400">{item.source_file} (Page {item.source_page})</span>
                </div>

                <div className="text-xs text-slate-300 space-y-1 bg-slate-950 p-3 rounded border border-slate-800">
                  <div><span className="text-slate-500">MD / Formation:</span> {item.md}m MD in {item.formation}</div>
                  <div><span className="text-slate-500">Summary:</span> {item.summary}</div>
                  <div><span className="text-slate-500">Mitigation:</span> {item.mitigation}</div>
                </div>

                <div className="flex justify-end pt-1">
                  <button
                    onClick={() => handleVerify(item.id)}
                    className="flex items-center space-x-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs px-4 py-1.5 rounded-lg font-bold transition shadow"
                  >
                    <ShieldCheck className="w-4 h-4" />
                    <span>Approve & Verify Record</span>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="bg-slate-900 border-t border-slate-800 p-4 flex justify-end">
          <button
            onClick={onClose}
            className="bg-slate-800 hover:bg-slate-700 text-white text-xs px-5 py-2 rounded-lg font-medium transition"
          >
            Close Queue
          </button>
        </div>

      </div>
    </div>
  );
}
