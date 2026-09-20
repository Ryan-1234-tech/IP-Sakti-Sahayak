"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Sparkles,
  ArrowRight,
  Shield,
  UploadCloud,
  MessageSquare,
  FileText,
  Clock,
  CheckCircle,
  AlertTriangle,
  HelpCircle
} from "lucide-react";

import AppShell from "@/components/layout/AppShell";
import WizardModal from "@/components/dashboard/WizardModal";
import { getUser, greeting, UserProfile } from "@/lib/auth";
import { getAllSessions, HistorySession } from "@/lib/history";

const IP_TYPES = [
  {
    id: "patent",
    icon: "🔬",
    title: "Patent Protection",
    desc: "Inventions, chemical & Ayurvedic processes, formulations",
    prompt: "I want to check patent eligibility for my technical invention under the Indian Patents Act 1970."
  },
  {
    id: "trademark",
    icon: "™️",
    title: "Trademark & Brand",
    desc: "Brand names, logos, slogans, Class 5 pharmaceuticals",
    prompt: "How do I register a Trademark for my AYUSH brand under the Trade Marks Act 1999?"
  },
  {
    id: "copyright",
    icon: "©️",
    title: "Copyright & Content",
    desc: "Manuals, software code, label artwork, research papers",
    prompt: "What is the procedure for registering Copyright for my product documentation in India?"
  },
  {
    id: "tk",
    icon: "🌿",
    title: "Traditional Knowledge",
    desc: "Herbal formulations, TKDL prior-art, Section 3(p) compliance",
    prompt: "How do I ensure my herbal formulation complies with TKDL and Section 3(p) of the Patents Act?"
  }
];

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [showWizard, setShowWizard] = useState(false);
  const [history, setHistory] = useState<HistorySession[]>([]);

  useEffect(() => {
    const u = getUser();
    if (!u) {
      router.push("/login");
    } else {
      setUser(u);
      setHistory(getAllSessions());
    }
  }, [router]);

  if (!user) return null;

  return (
    <AppShell>
      <div className="h-full overflow-y-auto p-8 max-w-6xl mx-auto space-y-8">
        
        {/* ── 1. Personalized Greeting Banner ── */}
        <div className="bg-gradient-to-r from-[#0c1911] via-emerald-950 to-slate-900 rounded-2xl p-6 text-white shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl" />
          
          <div className="space-y-1 relative z-10">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-600/30 text-emerald-300 border border-emerald-500/40">
                {user.role}
              </span>
              <span className="text-xs text-slate-400">• {user.org || "Independent"}</span>
            </div>
            <h1 className="font-bold text-2xl text-white">{greeting(user.name)}</h1>
            <p className="text-xs text-slate-300 max-w-xl">
              What compliance or IP guidance do you need for your product today? Every answer is backed by Indian legal gazettes.
            </p>
          </div>

          <button
            onClick={() => setShowWizard(true)}
            className="flex items-center gap-2 px-5 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl shadow-md transition-all hover:scale-105 flex-shrink-0 relative z-10"
          >
            <Sparkles size={16} />
            <span>"What IP Do I Need?" Wizard</span>
          </button>
        </div>

        {/* ── 2. Quick Action Feature Grid ── */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-bold text-slate-900">Select IP Protection Category</h2>
            <span className="text-xs text-slate-500">Click a card to launch a guided AI consultation</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {IP_TYPES.map((card) => (
              <div
                key={card.id}
                onClick={() => router.push(`/chat?prompt=${encodeURIComponent(card.prompt)}`)}
                className="bg-white rounded-2xl border border-slate-200 p-5 hover:border-emerald-500 hover:shadow-md transition-all cursor-pointer group flex flex-col justify-between"
              >
                <div>
                  <div className="text-3xl mb-3">{card.icon}</div>
                  <h3 className="font-bold text-sm text-slate-900 group-hover:text-emerald-700 transition-colors mb-1">
                    {card.title}
                  </h3>
                  <p className="text-xs text-slate-500 leading-relaxed">{card.desc}</p>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-emerald-700">
                  <span>Start Consultation</span>
                  <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ── 3. Document Analysis & Consultation Section ── */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Ask AI Prompt Card */}
          <div
            onClick={() => router.push("/chat")}
            className="bg-white rounded-2xl border border-slate-200 p-6 hover:border-emerald-500 hover:shadow-md transition-all cursor-pointer group flex items-start gap-4"
          >
            <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center flex-shrink-0">
              <MessageSquare size={24} />
            </div>
            <div>
              <h3 className="font-bold text-base text-slate-900 group-hover:text-emerald-700">
                Ask Legal &amp; AYUSH Advisor
              </h3>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Type natural queries about patent validity, trademark class search, Form 25-D renewal, or label claims.
              </p>
              <span className="inline-flex items-center gap-1 text-xs font-bold text-emerald-700 mt-3">
                Open Prompt Interface <ArrowRight size={13} />
              </span>
            </div>
          </div>

          {/* Upload PDF Card */}
          <div
            onClick={() => router.push("/chat")}
            className="bg-white rounded-2xl border border-slate-200 p-6 hover:border-emerald-500 hover:shadow-md transition-all cursor-pointer group flex items-start gap-4"
          >
            <div className="w-12 h-12 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center flex-shrink-0">
              <UploadCloud size={24} />
            </div>
            <div>
              <h3 className="font-bold text-base text-slate-900 group-hover:text-amber-700">
                Scan Government Notice / PDF
              </h3>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Upload a Trademark Examination Report, Patent Office Action, or label artwork to extract requirements.
              </p>
              <span className="inline-flex items-center gap-1 text-xs font-bold text-amber-700 mt-3">
                Upload &amp; Analyze PDF <ArrowRight size={13} />
              </span>
            </div>
          </div>
        </div>

        {/* ── 4. Recent Chat Sessions ── */}
        {history.length > 0 && (
          <div className="bg-white rounded-2xl border border-slate-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                <Clock size={16} className="text-slate-500" />
                <span>Recent Consultations</span>
              </h3>
              <button
                onClick={() => router.push("/chat")}
                className="text-xs text-emerald-700 font-semibold hover:underline"
              >
                View all
              </button>
            </div>

            <div className="space-y-2">
              {history.slice(0, 3).map((sess) => (
                <div
                  key={sess.id}
                  onClick={() => router.push(`/chat?session=${sess.id}`)}
                  className="flex items-center justify-between p-3 rounded-xl border border-slate-100 hover:bg-slate-50 transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center text-xs font-bold">
                      IP
                    </div>
                    <div>
                      <p className="text-xs font-bold text-slate-900">{sess.title}</p>
                      <p className="text-[10px] text-slate-400">
                        {new Date(sess.createdAt).toLocaleDateString()} • {sess.messages.length} messages
                      </p>
                    </div>
                  </div>
                  <ArrowRight size={14} className="text-slate-400" />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── 5. Legal Trust Layer Disclaimer ── */}
        <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 flex items-start gap-3 text-xs text-amber-800">
          <AlertTriangle size={18} className="text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-bold mb-0.5">Statutory Information Disclaimer</p>
            <p className="text-[11px] text-amber-700 leading-relaxed">
              IP-SAKTI Sahayak is an AI digital twin trained on Indian legal and AYUSH regulatory gazettes. Content generated is for decision-support and educational purposes and does not constitute formal legal advice.
            </p>
          </div>
        </div>

      </div>

      {/* ── Wizard Modal ── */}
      {showWizard && <WizardModal onClose={() => setShowWizard(false)} />}
    </AppShell>
  );
}
