"use client";

import { useState } from "react";
import { ExternalLink, Shield, Scale } from "lucide-react";
import { Risk } from "@/lib/risk-data";

interface Props {
  risk: Risk | null;
  onEscalate: (id: string) => void;
}

export default function Inspector({ risk, onEscalate }: Props) {
  const [showConfirm, setShowConfirm] = useState(false);
  const [escalated, setEscalated] = useState(false);

  const handleEscalate = () => {
    setEscalated(true);
    setShowConfirm(false);
    if (risk) onEscalate(risk.id);
  };

  // Empty state
  if (!risk) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center gap-3 py-16 px-6">
        <div className="w-14 h-14 rounded-2xl bg-slate-100 flex items-center justify-center mb-2">
          <svg width={28} height={28} viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth={1.5}>
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="12" y1="12" x2="12" y2="16" />
            <line x1="10" y1="14" x2="14" y2="14" />
          </svg>
        </div>
        <p className="text-sm font-semibold text-slate-500">No risk selected</p>
        <p className="text-xs text-slate-400 max-w-[200px] leading-relaxed">
          Pick a card from the radar feed to inspect verified evidence and its mitigation plan.
        </p>
      </div>
    );
  }

  const isEscalated = risk.escalated || escalated;

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      {/* ── Header ──────────────────────────────── */}
      <div className="px-6 pt-6 pb-4 border-b border-slate-100">
        <p className="text-[10px] font-bold uppercase tracking-widest text-emerald-600 mb-1">
          Explainability &amp; Action
        </p>
        <h2 className="font-display text-lg font-bold text-slate-900 leading-snug mb-3">
          {risk.title}
        </h2>
        <div className="flex flex-wrap gap-2">
          <span className="px-3 py-1 rounded-full bg-slate-100 text-xs text-slate-600 font-medium border border-slate-200">
            {risk.category}
          </span>
          <span className="px-3 py-1 rounded-full bg-slate-100 text-xs text-slate-600 font-medium border border-slate-200">
            Confidence {risk.confidence}%
          </span>
          <span className="px-3 py-1 rounded-full bg-slate-100 text-xs text-slate-600 font-medium border border-slate-200">
            Due {risk.deadline}
          </span>
        </div>
      </div>

      {/* ── Verified Evidence ────────────────────── */}
      <div className="px-6 py-5">
        <div className="flex items-center gap-2 mb-3">
          <svg width={15} height={15} viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth={2.5}>
            <polyline points="9 11 12 14 22 4" />
            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
          </svg>
          <p className="text-[11px] font-bold uppercase tracking-widest text-slate-500">
            Verified Evidence
          </p>
        </div>

        <div className="rounded-xl bg-emerald-50/60 border border-emerald-200 p-4 relative">
          <div className="flex items-start justify-between gap-3 mb-3">
            <h4 className="text-sm font-bold text-slate-800 leading-snug pr-2">
              {risk.evidence.clause}
            </h4>
            <a
              href={risk.evidence.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-shrink-0 text-emerald-600 hover:text-emerald-700 transition-colors"
              title="Open source"
            >
              <ExternalLink size={15} />
            </a>
          </div>
          <blockquote className="text-xs text-slate-600 italic leading-relaxed border-l-2 border-emerald-300 pl-3 mb-2">
            {risk.evidence.excerpt}
          </blockquote>
          <p className="text-[11px] text-slate-400">Source: {risk.evidence.source}</p>
        </div>
      </div>

      {/* ── Mitigation Plan ──────────────────────── */}
      <div className="px-6 pb-5">
        <div className="flex items-center gap-2 mb-3">
          <Scale size={14} className="text-amber-500" />
          <p className="text-[11px] font-bold uppercase tracking-widest text-slate-500">
            Actionable Mitigation Plan
          </p>
        </div>

        <div className="flex flex-col gap-2">
          {risk.mitigation.map((step, i) => (
            <div
              key={i}
              className="flex items-start gap-3 bg-white rounded-xl border border-slate-200 px-4 py-3 shadow-xs"
            >
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-emerald-100 text-emerald-700 text-xs font-bold flex items-center justify-center mt-0.5">
                {i + 1}
              </span>
              <p className="text-sm text-slate-700 leading-relaxed">{step}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── Spacer ──────────────────────────────── */}
      <div className="flex-1" />

      {/* ── Escalate CTA ────────────────────────── */}
      <div className="px-6 pb-6">
        {!isEscalated ? (
          <>
            {!showConfirm ? (
              <button
                onClick={() => setShowConfirm(true)}
                className="w-full flex items-center justify-center gap-2 bg-emerald-700 hover:bg-emerald-600 active:bg-emerald-800 text-white font-semibold text-sm py-3.5 rounded-xl transition-colors shadow-md"
              >
                <Shield size={16} />
                Escalate to Legal Expert
              </button>
            ) : (
              <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 animate-fade-up">
                <p className="text-sm font-semibold text-amber-800 mb-1">Confirm Escalation</p>
                <p className="text-xs text-amber-700 mb-4">
                  This will flag the risk for legal expert review. The case brief will be prepared automatically.
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={handleEscalate}
                    className="flex-1 bg-emerald-700 hover:bg-emerald-600 text-white text-sm font-semibold py-2 rounded-lg transition-colors"
                  >
                    Confirm
                  </button>
                  <button
                    onClick={() => setShowConfirm(false)}
                    className="flex-1 border border-slate-300 text-slate-600 hover:bg-slate-50 text-sm font-medium py-2 rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="w-full flex items-center justify-center gap-2 bg-slate-100 border border-slate-200 text-slate-500 font-semibold text-sm py-3.5 rounded-xl">
            <Shield size={16} className="text-emerald-500" />
            Escalated to Legal Panel
          </div>
        )}
      </div>
    </div>
  );
}
