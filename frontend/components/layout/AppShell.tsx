"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import {
  Leaf,
  LayoutDashboard,
  MessageSquare,
  UploadCloud,
  LogOut,
  UserCheck,
  Sparkles,
  Shield,
  Clock,
  Globe,
  Search,
} from "lucide-react";
import { getUser, clearUser, UserProfile } from "@/lib/auth";
import { useJurisdiction } from "@/lib/jurisdiction";
import LanguageSelector from "@/components/shared/LanguageSelector";
import StatusDot from "@/components/shared/StatusDot";
import HistorySidebar from "@/components/chat/HistorySidebar";

interface Props {
  children: React.ReactNode;
}

export default function AppShell({ children }: Props) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [currentLang, setCurrentLang] = useState("en");
  const { jurisdiction, setJurisdiction } = useJurisdiction();

  useEffect(() => {
    const u = getUser();
    if (!u && pathname !== "/login") {
      router.push("/login");
    } else if (u) {
      setUser(u);
      setCurrentLang(u.language || "en");
    }
  }, [pathname, router]);

  const handleLogout = () => {
    clearUser();
    router.push("/login");
  };

  const handleLangChange = (code: string) => {
    setCurrentLang(code);
    if (user) {
      const updated = { ...user, language: code };
      setUser(updated);
      localStorage.setItem("ipsakti_user", JSON.stringify(updated));
    }
  };

  if (pathname === "/login") {
    return <>{children}</>;
  }

  const navItems = [
    { label: "MSME Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { label: "Identify My IP", path: "/ip-recommender", icon: Sparkles },
    { label: "Patentability Pre-Screen", path: "/patentability", icon: UserCheck },
    { label: "AYUSH & TK Assessor", path: "/tk-risk", icon: Leaf },
    { label: "Biological Resource & ABS Assessor", path: "/biomaterial", icon: UploadCloud },
    { label: "TKDL & Prior Art Discovery", path: "/tk-prior-art", icon: Search },
    { label: "Document & Deadlines", path: "/document-analyzer", icon: Clock },
    { label: "MSME IP Health Check", path: "/msme-health", icon: Shield },
    { label: "IP Roadmap & Costs", path: "/roadmap-costs", icon: LayoutDashboard },
    { label: "Legal Provision Explainer", path: "/legal-explainer", icon: MessageSquare },
    { label: "Legal & AYUSH AI Chat", path: "/chat", icon: MessageSquare },
  ];

  return (
    <div className="flex h-screen w-full min-h-0 bg-slate-50 text-slate-900 font-sans overflow-hidden">
      {/* ── Persistent Left Navigation Sidebar ── */}
      <aside className="w-64 bg-[#0c1911] text-white flex flex-col h-full flex-shrink-0 border-r border-emerald-950 select-none">
        {/* Fixed Header: Logo Brand */}
        <div className="flex items-center gap-3 px-4 py-4 flex-shrink-0 border-b border-white/5 bg-[#0a150e]">
          <div className="w-10 h-10 rounded-xl bg-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-900/50 flex-shrink-0">
            <Leaf size={22} className="text-white" />
          </div>
          <div className="min-w-0">
            <h1 className="font-bold text-base leading-tight truncate">IP-SAKTI Sahayak</h1>
            <p className="text-[11px] text-emerald-400 truncate">Source-Cited IP &amp; AYUSH</p>
          </div>
        </div>

        {/* Scrollable Middle Section: Nav Items + User Profile Context + Chat History */}
        <div className="flex-1 min-h-0 overflow-y-auto p-3 space-y-4">
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = pathname === item.path;
              return (
                <button
                  key={item.path}
                  onClick={() => router.push(item.path)}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium transition-colors text-left ${
                    active
                      ? "bg-emerald-700/40 text-emerald-300 border border-emerald-600/50 font-bold"
                      : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
                  }`}
                >
                  <Icon size={16} className={active ? "text-emerald-400 flex-shrink-0" : "flex-shrink-0"} />
                  <span className="truncate">{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Active User Context Badge */}
          {user && (
            <div className="bg-white/5 border border-white/10 rounded-xl p-3.5">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Profile Context</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-900/60 text-emerald-300 font-bold border border-emerald-700/50">
                  {user.role}
                </span>
              </div>
              <p className="text-xs font-bold text-white truncate">{user.name}</p>
              <p className="text-[11px] text-slate-400 truncate">{user.org || "Independent Developer"}</p>
            </div>
          )}

          {/* Session Chat History Component */}
          {pathname === "/chat" && <HistorySidebar />}
        </div>

        {/* Fixed Footer: Backend Health Status + Logout */}
        <div className="border-t border-white/10 p-3.5 space-y-2 flex-shrink-0 bg-[#0a150e]">
          <StatusDot />
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-2.5 py-2 rounded-lg text-xs font-medium text-slate-400 hover:text-rose-400 hover:bg-rose-950/20 transition-colors"
          >
            <LogOut size={14} />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* ── Main View Area with Topbar Header ── */}
      <div className="flex-1 flex flex-col h-full min-h-0 min-w-0 bg-slate-50">
        <header className="h-16 border-b border-slate-200 bg-white flex items-center justify-between px-6 flex-shrink-0">
          <div className="flex items-center gap-3">
            <h2 className="text-sm font-bold text-slate-900">
              {pathname === "/dashboard"
                ? "Compliance & IP Dashboard"
                : pathname === "/tk-risk"
                ? "AYUSH & Traditional Knowledge Assessor"
                : pathname === "/biomaterial"
                ? "Biological Resource & ABS Assessor"
                : pathname === "/tk-prior-art"
                ? "TKDL & Prior Art Discovery Aid"
                : "Legal & AYUSH Consultation Engine"}
            </h2>
          </div>

          <div className="flex items-center gap-4">
            {/* Step 4: Shared Jurisdiction Toggle */}
            <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200">
              <button
                type="button"
                id="jurisdiction-india-toggle"
                onClick={() => setJurisdiction("INDIA")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  jurisdiction === "INDIA"
                    ? "bg-emerald-600 text-white shadow-xs"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                <span>🇮🇳</span>
                <span>INDIA</span>
              </button>
              <button
                type="button"
                id="jurisdiction-international-toggle"
                onClick={() => setJurisdiction("INTERNATIONAL")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  jurisdiction === "INTERNATIONAL"
                    ? "bg-indigo-600 text-white shadow-xs"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                <span>🌐</span>
                <span>INTERNATIONAL</span>
              </button>
            </div>

            {/* Multilingual Selector */}
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-500">Language:</span>
              <LanguageSelector value={currentLang} onChange={handleLangChange} />
            </div>

            {/* Profile Avatar Chip */}
            {user && (
              <div className="flex items-center gap-2 pl-3 border-l border-slate-200">
                <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 font-bold text-xs flex items-center justify-center">
                  {user.name.charAt(0).toUpperCase()}
                </div>
                <div className="hidden sm:block text-left">
                  <p className="text-xs font-bold text-slate-900 leading-tight">{user.name}</p>
                  <p className="text-[10px] text-slate-500">{user.role}</p>
                </div>
              </div>
            )}
          </div>
        </header>

        {/* Content Children */}
        <main className="flex-1 min-h-0 overflow-hidden">{children}</main>
      </div>
    </div>
  );
}
