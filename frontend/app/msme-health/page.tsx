"use client";

import { useState } from "react";
import AppShell from "@/components/layout/AppShell";
import { Shield, CheckCircle, AlertTriangle, ArrowRight, Activity, Sparkles } from "lucide-react";

export default function MSMEHealthPage() {
  const [q1, setQ1] = useState(true);   // Registered Business
  const [q2, setQ2] = useState(true);   // Brand Name
  const [q3, setQ3] = useState(true);   // Logo
  const [q4, setQ4] = useState(true);   // Unique Product
  const [q5, setQ5] = useState(true);   // Tech Innovation
  const [q6, setQ6] = useState(true);   // Product Docs
  const [q7, setQ7] = useState(false);  // Confidential Info / NDA
  const [q8, setQ8] = useState(false);  // Searched Patents
  const [q9, setQ9] = useState(true);   // Searched Trademarks
  const [q10, setQ10] = useState(true); // Biological Resources
  const [q11, setQ11] = useState(true); // TK Involved

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAssess = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/features/msme-health-check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          has_registered_business: q1,
          has_brand_name: q2,
          has_logo: q3,
          has_unique_product: q4,
          has_tech_innovation: q5,
          has_product_docs: q6,
          has_confidential_info: q7,
          has_searched_patents: q8,
          has_searched_trademarks: q9,
          uses_biological_resources: q10,
          traditional_knowledge_involved: q11,
        }),
      });
      const data = await res.json();
      setResult(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <div className="h-full overflow-y-auto p-8 max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-gradient-to-r from-[#0c1911] via-slate-900 to-emerald-950 rounded-2xl p-6 text-white shadow-xl flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-600/30 text-emerald-300 border border-emerald-500/40">
                MSME &amp; Startup Diagnostic Engine
              </span>
            </div>
            <h1 className="font-bold text-xl text-white">MSME IP Health Check</h1>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl">
              Answer 11 diagnostic questions to calculate your transparent MSME IP Readiness Score (0–100) and receive actionable compliance steps.
            </p>
          </div>
          <Activity size={32} className="text-emerald-400 opacity-80 flex-shrink-0" />
        </div>

        {/* Questionnaire */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <h2 className="font-bold text-xs uppercase tracking-wider text-slate-800 border-b border-slate-100 pb-2">
            IP Readiness Questions
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <label className="flex items-center justify-between p-3.5 rounded-xl border border-slate-200 bg-slate-50 cursor-pointer">
              <span className="font-bold text-slate-800">1. Registered Business Entity (UDYAM/Company)?</span>
              <input type="checkbox" checked={q1} onChange={(e) => setQ1(e.target.checked)} className="w-4 h-4 text-emerald-600 rounded" />
            </label>
            <label className="flex items-center justify-between p-3.5 rounded-xl border border-slate-200 bg-slate-50 cursor-pointer">
              <span className="font-bold text-slate-800">2. Unique Brand Name for Product/Service?</span>
              <input type="checkbox" checked={q2} onChange={(e) => setQ2(e.target.checked)} className="w-4 h-4 text-emerald-600 rounded" />
            </label>
            <label className="flex items-center justify-between p-3.5 rounded-xl border border-slate-200 bg-slate-50 cursor-pointer">
              <span className="font-bold text-slate-800">3. Custom Logo / Visual Brand Mark?</span>
              <input type="checkbox" checked={q3} onChange={(e) => setQ3(e.target.checked)} className="w-4 h-4 text-emerald-600 rounded" />
            </label>
            <label className="flex items-center justify-between p-3.5 rounded-xl border border-slate-200 bg-slate-50 cursor-pointer">
              <span className="font-bold text-slate-800">4. Unique Physical Shape or Packaging Design?</span>
              <input type="checkbox" checked={q4} onChange={(e) => setQ4(e.target.checked)} className="w-4 h-4 text-emerald-600 rounded" />
            </label>
            <label className="flex items-center justify-between p-3.5 rounded-xl border border-slate-200 bg-slate-50 cursor-pointer">
              <span className="font-bold text-slate-800">5. Technical Process or Formulation Innovation?</span>
              <input type="checkbox" checked={q5} onChange={(e) => setQ5(e.target.checked)} className="w-4 h-4 text-emerald-600 rounded" />
            </label>
            <label className="flex items-center justify-between p-3.5 rounded-xl border border-slate-200 bg-slate-50 cursor-pointer">
              <span className="font-bold text-slate-800">6. Written Product Documentation / User Manual?</span>
              <input type="checkbox" checked={q6} onChange={(e) => setQ6(e.target.checked)} className="w-4 h-4 text-emerald-600 rounded" />
            </label>
            <label className="flex items-center justify-between p-3.5 rounded-xl border border-slate-200 bg-slate-50 cursor-pointer">
              <span className="font-bold text-slate-800">7. Confidential Info Protected via NDAs?</span>
              <input type="checkbox" checked={q7} onChange={(e) => setQ7(e.target.checked)} className="w-4 h-4 text-emerald-600 rounded" />
            </label>
            <label className="flex items-center justify-between p-3.5 rounded-xl border border-slate-200 bg-slate-50 cursor-pointer">
              <span className="font-bold text-slate-800">8. Prior-Art Patent Search Conducted?</span>
              <input type="checkbox" checked={q8} onChange={(e) => setQ8(e.target.checked)} className="w-4 h-4 text-emerald-600 rounded" />
            </label>
            <label className="flex items-center justify-between p-3.5 rounded-xl border border-slate-200 bg-slate-50 cursor-pointer">
              <span className="font-bold text-slate-800">9. Trademark Availability Search Conducted?</span>
              <input type="checkbox" checked={q9} onChange={(e) => setQ9(e.target.checked)} className="w-4 h-4 text-emerald-600 rounded" />
            </label>
            <label className="flex items-center justify-between p-3.5 rounded-xl border border-slate-200 bg-slate-50 cursor-pointer">
              <span className="font-bold text-slate-800">10. Uses Botanical / Biological Resources?</span>
              <input type="checkbox" checked={q10} onChange={(e) => setQ10(e.target.checked)} className="w-4 h-4 text-emerald-600 rounded" />
            </label>
            <label className="flex items-center justify-between p-3.5 rounded-xl border border-slate-200 bg-slate-50 cursor-pointer md:col-span-2">
              <span className="font-bold text-slate-800">11. Traditional Knowledge / AYUSH Medicinal Formulation Involved?</span>
              <input type="checkbox" checked={q11} onChange={(e) => setQ11(e.target.checked)} className="w-4 h-4 text-emerald-600 rounded" />
            </label>
          </div>

          <div className="flex justify-end">
            <button
              onClick={handleAssess}
              disabled={loading}
              className="flex items-center gap-2 px-6 py-2.5 bg-emerald-700 hover:bg-emerald-600 text-white font-bold text-xs rounded-xl shadow transition-all disabled:opacity-50"
            >
              {loading ? "Calculating Health Score..." : "Calculate MSME IP Health Score"}
              <ArrowRight size={14} />
            </button>
          </div>
        </div>

        {/* Results Gauge */}
        {result && (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
              <div className="flex flex-col md:flex-row items-center justify-between gap-6 border-b border-slate-100 pb-6">
                <div>
                  <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider">MSME IP Health Score</h2>
                  <div className="flex items-baseline gap-2 mt-1">
                    <span className="text-4xl font-extrabold text-slate-900">{result.overall_score}</span>
                    <span className="text-base text-slate-500 font-bold">/ 100</span>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">Calculated via deterministic statutory scoring algorithm</p>
                </div>

                <div className="flex-1 max-w-md w-full bg-slate-100 rounded-full h-4 overflow-hidden p-0.5 border border-slate-200">
                  <div
                    className="bg-gradient-to-r from-emerald-500 to-emerald-700 h-full rounded-full transition-all duration-700"
                    style={{ width: `${result.overall_score}%` }}
                  />
                </div>
              </div>

              {/* Sub Breakdown */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-center">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">Patent</span>
                  <p className="text-sm font-bold text-emerald-700 mt-0.5">{result.patent_readiness}%</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-center">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">Trademark</span>
                  <p className="text-sm font-bold text-emerald-700 mt-0.5">{result.trademark_readiness}%</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-center">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">Design</span>
                  <p className="text-sm font-bold text-emerald-700 mt-0.5">{result.design_readiness}%</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-center">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">Copyright</span>
                  <p className="text-sm font-bold text-emerald-700 mt-0.5">{result.copyright_readiness}%</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-center col-span-2 md:col-span-1">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">Docs / NDA</span>
                  <p className="text-sm font-bold text-emerald-700 mt-0.5">{result.documentation_readiness}%</p>
                </div>
              </div>

              {/* Strengths & Risks */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200">
                  <h3 className="font-bold text-xs text-emerald-900 mb-2 flex items-center gap-1.5">
                    <CheckCircle size={15} className="text-emerald-600" />
                    <span>Identified IP Strengths</span>
                  </h3>
                  <ul className="space-y-1 text-xs text-emerald-800">
                    {result.strengths?.map((s: string, idx: number) => (
                      <li key={idx}>• {s}</li>
                    ))}
                  </ul>
                </div>

                <div className="p-4 rounded-xl bg-rose-50 border border-rose-200">
                  <h3 className="font-bold text-xs text-rose-900 mb-2 flex items-center gap-1.5">
                    <AlertTriangle size={15} className="text-rose-600" />
                    <span>Identified Compliance Risks</span>
                  </h3>
                  <ul className="space-y-1 text-xs text-rose-800">
                    {result.risks?.map((r: string, idx: number) => (
                      <li key={idx}>• {r}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Actions */}
              <div>
                <h3 className="font-bold text-xs text-slate-800 uppercase mb-2">Recommended Next Actions</h3>
                <div className="space-y-2">
                  {result.recommended_actions?.map((act: string, idx: number) => (
                    <div key={idx} className="flex items-center gap-2 text-xs text-slate-800 bg-slate-50 p-3 rounded-xl border border-slate-200 font-medium">
                      <ArrowRight size={14} className="text-emerald-600 flex-shrink-0" />
                      <span>{act}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
