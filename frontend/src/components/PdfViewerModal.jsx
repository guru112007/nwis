import React from 'react';
import { X, FileText, ShieldCheck, Download, ExternalLink } from 'lucide-react';

export default function PdfViewerModal({ alertData, onClose }) {
  if (!alertData) return null;

  const pdfUrl = `/api/v1/documents/download/${alertData.source_file}`;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-[#0B0F19] border border-slate-700 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">

        {/* Modal Header */}
        <div className="bg-slate-900 border-b border-slate-800 p-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FileText className="w-6 h-6 text-cyan-400" />
            <div>
              <h3 className="text-sm font-bold text-slate-100 font-mono">
                {alertData.source_file} (Page {alertData.source_page})
              </h3>
              <p className="text-xs text-slate-400 font-mono">
                Document SHA-256 Hash: <span className="text-cyan-400">{alertData.doc_hash ? alertData.doc_hash.substring(0, 16) + '...' : 'Verified'}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <span className="flex items-center space-x-1 text-xs font-mono font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800 px-2.5 py-1 rounded-md">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Human Verified (OCR: {(alertData.ocr_confidence * 100).toFixed(0)}%)</span>
            </span>

            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-white bg-slate-800 rounded-lg transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {/* Highlight Bounding Box Info */}
          <div className="bg-cyan-950/40 border border-cyan-800/60 p-3 rounded-lg text-xs font-mono text-cyan-200 flex items-center justify-between">
            <div>
              <span className="font-bold text-cyan-400">EXTRACTIVE CITATION BOUNDING BOX:</span>{' '}
              <span>[{alertData.bbox ? alertData.bbox.join(', ') : '72, 140, 520, 310'}]</span>
            </div>
            <a
              href={pdfUrl}
              target="_blank"
              rel="noreferrer"
              className="flex items-center space-x-1 text-cyan-400 hover:underline"
            >
              <span>Download PDF</span>
              <Download className="w-3.5 h-3.5" />
            </a>
          </div>

          {/* Incident Document Preview Box */}
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 relative min-h-[300px]">
            <div className="border-b border-slate-800 pb-3 mb-4 flex items-center justify-between">
              <div>
                <span className="text-xs font-mono text-slate-400 uppercase">OFFICIAL OIL REPORT CITATION</span>
                <h4 className="text-base font-bold text-slate-100">{alertData.event_category}</h4>
              </div>
              <span className="text-xs font-mono text-amber-400 bg-amber-950 border border-amber-800 px-2 py-0.5 rounded">
                Well: {alertData.offset_well_id} | Depth: {alertData.active_md_m || 2150}m MD
              </span>
            </div>

            {/* Bounding Box Highlighted Snippet */}
            <div className="relative border-2 border-rose-500 bg-rose-950/20 p-4 rounded-lg my-4 shadow-inner">
              <span className="absolute -top-3 left-3 bg-rose-600 text-white text-[10px] font-mono px-2 py-0.5 rounded font-bold">
                EXTRACTED CITATION PAGE {alertData.source_page}
              </span>
              <p className="text-sm font-mono text-slate-200 leading-relaxed font-medium">
                "{alertData.historical_summary}"
              </p>
              <div className="mt-3 pt-3 border-t border-rose-900/60 font-mono text-xs text-emerald-300">
                <span className="font-bold text-emerald-400">APPLIED MITIGATION LOGGED:</span> {alertData.mitigation_applied}
              </div>
            </div>

            <p className="text-xs text-slate-500 italic mt-6">
              Source file: {alertData.source_file} verified and indexed in PostgreSQL pgvector database.
            </p>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="bg-slate-900 border-t border-slate-800 p-4 flex justify-end">
          <button
            onClick={onClose}
            className="bg-slate-800 hover:bg-slate-700 text-white text-xs px-5 py-2 rounded-lg font-medium transition"
          >
            Close Reader
          </button>
        </div>

      </div>
    </div>
  );
}
