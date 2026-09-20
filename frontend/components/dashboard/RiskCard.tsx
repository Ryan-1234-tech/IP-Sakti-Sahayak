"use client";

import { Flame, Wind, Shield } from "lucide-react";
import { Risk, daysUntil } from "@/lib/risk-data";

interface Props {
  risk: Risk;
  isSelected: boolean;
  onClick: () => void;
}

const PRIORITY_STYLES: Record<string, string> = {
  HIGH:   "bg-rose-50 text-rose-600 border-rose-200",
  MEDIUM: "bg-amber-50 text-amber-600 border-amber-200",
  LOW:    "bg-emerald-50 text-emerald-600 border-emerald-200",
};

const PRIORITY_ICON: Record<string, React.ReactNode> = {
  HIGH:   <Flame size={12} />,
  MEDIUM: <Wind size={12} />,
  LOW:    <Wind size={12} />,
};

const BAR_COLOR: Record<string, string> = {
  HIGH:   "bg-amber-500",
  MEDIUM: "bg-emerald-600",
  LOW:    "bg-emerald-500",
};

export default function RiskCard({ risk, isSelected, onClick }: Props) {
  const days = daysUntil(risk.deadline);
  const isOverdue = days < 0;
  const isUrgent = days >= 0 && days <= 30;

  return (
    <button
      onClick={onClick}
      className={`w-full text-left rounded-2xl border p-5 transition-all duration-200 shadow-sm ${
        isSelected
          ? "border-emerald-400 ring-2 ring-emerald-200 bg-white"
          : "border-slate-200 bg-white hover:border-emerald-300 hover:shadow-md"
      }`}
    >
      {/* ── Top row: badges + score ─── */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center flex-wrap gap-2">
          {/* Priority badge */}
          <span
            className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold border ${
              PRIORITY_STYLES[risk.priority]
            }`}
          >
            {PRIORITY_ICON[risk.priority]}
            {risk.priority}
          </span>
          {/* Category badge */}
          <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">
            {risk.category}
          </span>
          {/* Escalated badge */}
          {risk.escalated && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border border-slate-300 text-slate-500 bg-white">
              <Shield size={10} />
              Escalated
            </span>
          )}
        </div>
        {/* Score */}
        <div className="text-right ml-4 flex-shrink-0">
          <p className="text-2xl font-bold text-slate-900 leading-none">{risk.score}</p>
          <p className="text-[10px] uppercase tracking-wider text-slate-400 mt-0.5">Risk Score</p>
        </div>
      </div>

      {/* ── Title & description ─── */}
      <h3 className="font-semibold text-slate-900 text-sm mb-1 leading-snug">{risk.title}</h3>
      <p className="text-xs text-slate-500 leading-relaxed mb-3 line-clamp-2">
        {risk.description}
      </p>

      {/* ── Meta row: confidence · deadline · id ─── */}
      <div className="flex items-center gap-4 text-xs text-slate-500 mb-3">
        <span className="flex items-center gap-1">
          {/* AI sparkle */}
          <svg width={13} height={13} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="text-emerald-500">
            <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" />
          </svg>
          <span>Confidence</span>
          <span className="font-bold text-slate-700">{risk.confidence}%</span>
        </span>
        <span
          className={`flex items-center gap-1 ${
            isOverdue ? "text-rose-600 font-semibold" : isUrgent ? "text-rose-500 font-semibold" : "text-slate-500"
          }`}
        >
          {/* Calendar icon */}
          <svg width={13} height={13} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
            <line x1="16" y1="2" x2="16" y2="6" />
            <line x1="8" y1="2" x2="8" y2="6" />
            <line x1="3" y1="10" x2="21" y2="10" />
          </svg>
          {risk.deadline}
          {" · "}
          {isOverdue ? "Overdue" : `${days}d`}
        </span>
        <span className="flex items-center gap-1">
          {/* Circle gauge */}
          <svg width={13} height={13} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="text-slate-400">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 6v6l4 2" />
          </svg>
          {risk.displayId}
        </span>
      </div>

      {/* ── Progress bar ─── */}
      <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${BAR_COLOR[risk.priority]}`}
          style={{ width: `${risk.score}%` }}
        />
      </div>
    </button>
  );
}
