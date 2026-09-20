"use client";

import { useState } from "react";
import { ChevronLeft, Shield, BarChart2, FileText, Users, Leaf } from "lucide-react";

type NavItem = "Risk Radar" | "Document Vault" | "Compliance Analytics" | "Expert Queue";

interface Props {
  activeNav: NavItem;
  onNavChange: (nav: NavItem) => void;
}

const NAV: { label: NavItem; icon: React.ReactNode }[] = [
  { label: "Risk Radar",           icon: <Shield size={18} /> },
  { label: "Document Vault",       icon: <FileText size={18} /> },
  { label: "Compliance Analytics", icon: <BarChart2 size={18} /> },
  { label: "Expert Queue",         icon: <Users size={18} /> },
];

export default function AppSidebar({ activeNav, onNavChange }: Props) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className="flex flex-col h-full bg-[#0e1b13] text-white transition-all duration-300 ease-in-out relative"
      style={{ width: collapsed ? 76 : 264 }}
    >
      {/* ── Brand ──────────────────────────────────── */}
      <div className="flex items-center gap-3 px-4 pt-6 pb-5">
        <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-emerald-600 flex items-center justify-center shadow-lg">
          <Leaf size={18} className="text-white" />
        </div>
        {!collapsed && (
          <div className="overflow-hidden">
            <p className="font-display font-bold text-sm leading-tight text-white whitespace-nowrap">
              IP-SAKTI Sahayak
            </p>
            <p className="text-[10px] text-emerald-400/80 whitespace-nowrap">
              Explainable Risk Radar
            </p>
          </div>
        )}
      </div>

      {/* ── Active product ─────────────────────────── */}
      {!collapsed && (
        <div className="mx-3 mb-4 rounded-lg bg-white/5 border border-white/8 px-3 py-2.5">
          <p className="text-[10px] uppercase tracking-widest text-slate-400 mb-0.5">
            Active Product
          </p>
          <p className="text-sm font-semibold text-white">Product #AY-2026-X</p>
        </div>
      )}

      {/* ── Engine badge ───────────────────────────── */}
      <div
        className={`mx-3 mb-5 flex items-center gap-2 rounded-lg border border-emerald-700/40 bg-emerald-900/20 px-3 py-2 ${
          collapsed ? "justify-center" : ""
        }`}
      >
        <Shield size={14} className="flex-shrink-0 text-emerald-400" />
        {!collapsed && (
          <span className="text-xs text-emerald-300 font-medium flex-1">
            AYUSH Legal Engine v2.4
          </span>
        )}
        {/* Pulsing green dot */}
        <span className="relative flex h-2 w-2 flex-shrink-0">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
        </span>
      </div>

      {/* ── Navigation ─────────────────────────────── */}
      <nav className="flex-1 flex flex-col gap-1 px-3">
        {NAV.map(({ label, icon }) => {
          const isActive = activeNav === label;
          return (
            <button
              key={label}
              onClick={() => onNavChange(label)}
              title={collapsed ? label : undefined}
              className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150 ${
                collapsed ? "justify-center" : ""
              } ${
                isActive
                  ? "bg-emerald-700/30 text-emerald-300 border border-emerald-600/40"
                  : "text-slate-400 hover:text-white hover:bg-white/5"
              }`}
            >
              <span className={isActive ? "text-emerald-400" : "text-slate-500"}>
                {icon}
              </span>
              {!collapsed && <span>{label}</span>}
            </button>
          );
        })}
      </nav>

      {/* ── Collapse toggle ────────────────────────── */}
      <button
        onClick={() => setCollapsed((c) => !c)}
        className="flex items-center gap-2 px-4 py-4 text-slate-400 hover:text-white text-sm transition-colors border-t border-white/5"
      >
        <ChevronLeft
          size={16}
          className={`transition-transform duration-300 ${collapsed ? "rotate-180" : ""}`}
        />
        {!collapsed && <span>Collapse</span>}
      </button>
    </aside>
  );
}
