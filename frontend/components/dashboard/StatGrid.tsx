"use client";

import { AlertTriangle, Calendar, UserCheck } from "lucide-react";

interface Stats {
  complianceScore: number;
  activeRisks: number;
  pendingDeadlines: number;
  escalations: number;
}

interface Props {
  stats: Stats;
  highCount: number;
  mediumCount: number;
  urgentLabel?: string;
}

// ── SVG ring gauge ─────────────────────────────────────────────────────────────
function RingGauge({ score }: { score: number }) {
  const r = 38;
  const circ = 2 * Math.PI * r;
  const fill = (score / 100) * circ;
  return (
    <svg width={88} height={88} viewBox="0 0 88 88" className="flex-shrink-0">
      {/* track */}
      <circle cx={44} cy={44} r={r} fill="none" stroke="#e5e7eb" strokeWidth={7} />
      {/* progress */}
      <circle
        cx={44}
        cy={44}
        r={r}
        fill="none"
        stroke="#059669"
        strokeWidth={7}
        strokeLinecap="round"
        strokeDasharray={`${fill} ${circ}`}
        transform="rotate(-90 44 44)"
        className="transition-all duration-700"
      />
      {/* label */}
      <text x={44} y={40} textAnchor="middle" className="font-bold" fontSize={18} fill="#111827" fontWeight={700}>
        {score}
      </text>
      <text x={44} y={54} textAnchor="middle" fontSize={10} fill="#6b7280">
        /100
      </text>
    </svg>
  );
}

export default function StatGrid({ stats, highCount, mediumCount, urgentLabel }: Props) {
  return (
    <div className="grid grid-cols-2 gap-4 mb-6">
      {/* Compliance Score */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 flex items-center gap-5 shadow-sm">
        <RingGauge score={stats.complianceScore} />
        <div>
          <p className="text-xs text-slate-500 font-medium mb-1">Total Compliance Score</p>
          <p className="text-3xl font-bold text-slate-900 leading-none">
            {stats.complianceScore}
            <span className="text-base text-slate-400 font-normal">/100</span>
          </p>
          <p className="text-xs text-emerald-600 font-medium mt-1.5">+6 pts since last scan</p>
        </div>
      </div>

      {/* Active Risks */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm relative overflow-hidden">
        <div className="absolute top-4 right-4 w-9 h-9 rounded-full bg-rose-50 flex items-center justify-center">
          <AlertTriangle size={17} className="text-rose-500" />
        </div>
        <p className="text-xs text-slate-500 font-medium mb-2">Active IP & AYUSH Risks</p>
        <p className="text-3xl font-bold text-slate-900">
          {stats.activeRisks}{" "}
          <span className="text-base font-medium text-slate-600">Active</span>
        </p>
        <p className="text-xs text-slate-400 mt-1">
          {highCount} high · {mediumCount} medium
        </p>
      </div>

      {/* Pending Deadlines */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm relative overflow-hidden">
        <div className="absolute top-4 right-4 w-9 h-9 rounded-full bg-amber-50 flex items-center justify-center">
          <Calendar size={17} className="text-amber-500" />
        </div>
        <p className="text-xs text-slate-500 font-medium mb-2">Pending Renewal Deadlines</p>
        <p className="text-3xl font-bold text-slate-900">
          {stats.pendingDeadlines}{" "}
          <span className="text-base font-medium text-slate-600">Urgent</span>
        </p>
        {urgentLabel && (
          <p className="text-xs text-slate-400 mt-1">{urgentLabel}</p>
        )}
      </div>

      {/* Escalations */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm relative overflow-hidden">
        <div className="absolute top-4 right-4 w-9 h-9 rounded-full bg-slate-100 flex items-center justify-center">
          <UserCheck size={17} className="text-slate-500" />
        </div>
        <p className="text-xs text-slate-500 font-medium mb-2">Expert Review Escalations</p>
        <p className="text-3xl font-bold text-slate-900">
          {stats.escalations}{" "}
          <span className="text-base font-medium text-slate-600">Escalated</span>
        </p>
        <p className="text-xs text-slate-400 mt-1">Assigned to legal panel</p>
      </div>
    </div>
  );
}
