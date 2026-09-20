import { useState } from "react";
import AppShell from "@/components/layout/AppShell";
import { useJurisdiction } from "@/lib/jurisdiction";
import { UserCheck, Shield, AlertTriangle, FileText, Download, CheckCircle, ArrowRight, BookOpen } from "lucide-react";

export default function PatentabilityPage() {
  const { jurisdiction } = useJurisdiction();
  const [title, setTitle] = useState("Synergistic Ayurvedic Anti-Inflammatory Topical Hydrogel");
  const [description, setDescription] = useState(
    "A topical hydrogel formulation combining standardized extracts of Turmeric (Curcuma longa), Ashwagandha (Withania somnifera), and Neem (Azadirachta indica) in a specific 3:2:1 ratio using nano-emulsion technology."
  );
  const [ingredients, setIngredients] = useState("Turmeric extract, Ashwagandha extract, Neem extract, Carbopol 940, Water");
  const [technicalProcess, setTechnicalProcess] = useState("Nano-emulsification followed by cold-gelation at 4°C.");
  const [claimedNew, setClaimedNew] = useState("Synergistic 3:2:1 extraction ratio providing Combination Index CI < 0.75 for COX-2 inhibition.");
  const [technicalAdvantage, setTechnicalAdvantage] = useState("4x increased skin penetration and 50% faster reduction in joint inflammation compared to individual extracts.");
  const [isTkInvolved, setIsTkInvolved] = useState(true);
  const [isBioInvolved, setIsBioInvolved] = useState(true);

  const [loading, setLoading] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleScreen = async () => {
    if (!title || !description) return;
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/features/patentability-prescreen", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          description,
          ingredients,
          technical_process: technicalProcess,
          claimed_new: claimedNew,
          technical_advantage: technicalAdvantage,
          is_tk_involved: isTkInvolved,
          is_biological_involved: isBioInvolved,
          jurisdiction: jurisdiction,
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

  const handleDownloadReport = async () => {
    setPdfLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/features/generate-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          applicant_name: "AYUSH Entrepreneur / Startup",
          invention_title: title,
          description: description,
          ingredients: ingredients,
        }),
      });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `IP_Assessment_Report_${title.slice(0, 15).replace(/\s+/g, "_")}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (e) {
      console.error("PDF download error", e);
    } finally {
      setPdfLoading(false);
    }
  };

  return (
    <AppShell>
      <div className="h-full overflow-y-auto p-8 max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-gradient-to-r from-[#0c1911] via-emerald-950 to-slate-900 rounded-2xl p-6 text-white shadow-xl flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-600/30 text-emerald-300 border border-emerald-500/40">
                Indian Patents Act 1970
              </span>
            </div>
            <h1 className="font-bold text-xl text-white">Patentability Pre-Screening &amp; Assessment</h1>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl">
              Evaluate preliminary Novelty, Inventive Step, Section 3(p) TKDL concerns, and Biological Diversity Act 2002 compliance before filing.
            </p>
          </div>

          <button
            onClick={handleDownloadReport}
            disabled={pdfLoading}
            className="flex items-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl shadow transition-all flex-shrink-0 disabled:opacity-50"
          >
            <Download size={15} />
            <span>{pdfLoading ? "Generating PDF..." : "Generate IP Assessment Report PDF"}</span>
          </button>
        </div>

        {/* Input Form */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Invention Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full text-xs p-3 rounded-xl border border-slate-300 bg-slate-50 text-slate-900 font-medium"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Ingredients / Biological Materials</label>
              <input
                type="text"
                value={ingredients}
                onChange={(e) => setIngredients(e.target.value)}
                className="w-full text-xs p-3 rounded-xl border border-slate-300 bg-slate-50 text-slate-900 font-medium"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Detailed Invention Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full text-xs p-3 rounded-xl border border-slate-300 bg-slate-50 text-slate-900"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Technical Process</label>
              <input
                type="text"
                value={technicalProcess}
                onChange={(e) => setTechnicalProcess(e.target.value)}
                className="w-full text-xs p-2.5 rounded-xl border border-slate-300 bg-slate-50 text-slate-900"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">What Is Claimed to Be New?</label>
              <input
                type="text"
                value={claimedNew}
                onChange={(e) => setClaimedNew(e.target.value)}
                className="w-full text-xs p-2.5 rounded-xl border border-slate-300 bg-slate-50 text-slate-900"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Expected Technical Advantage</label>
              <input
                type="text"
                value={technicalAdvantage}
                onChange={(e) => setTechnicalAdvantage(e.target.value)}
                className="w-full text-xs p-2.5 rounded-xl border border-slate-300 bg-slate-50 text-slate-900"
              />
            </div>
          </div>

          <div className="flex items-center gap-6 pt-2 border-t border-slate-100">
            <label className="flex items-center gap-2 cursor-pointer text-xs font-medium text-slate-700">
              <input
                type="checkbox"
                checked={isTkInvolved}
                onChange={(e) => setIsTkInvolved(e.target.checked)}
                className="w-4 h-4 text-emerald-600 rounded"
              />
              <span>Includes Traditional Knowledge / AYUSH Herb</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer text-xs font-medium text-slate-700">
              <input
                type="checkbox"
                checked={isBioInvolved}
                onChange={(e) => setIsBioInvolved(e.target.checked)}
                className="w-4 h-4 text-emerald-600 rounded"
              />
              <span>Uses Biological Resource Obtained from India</span>
            </label>
          </div>

          <div className="flex justify-end">
            <button
              onClick={handleScreen}
              disabled={loading}
              className="flex items-center gap-2 px-6 py-2.5 bg-emerald-700 hover:bg-emerald-600 text-white font-bold text-xs rounded-xl shadow transition-all disabled:opacity-50"
            >
              {loading ? "Running Analysis..." : "Run Patentability Pre-Screen"}
              <ArrowRight size={14} />
            </button>
          </div>
        </div>

        {/* Assessment Output */}
        {result && (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
              <h2 className="font-bold text-sm text-slate-900 uppercase tracking-wider border-b border-slate-100 pb-2">
                PATENTABILITY PRE-SCREEN RESULTS
              </h2>

              {/* Status Gauges */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-center">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">Novelty Score</span>
                  <p className="text-base font-extrabold text-emerald-700 mt-1">{result.novelty}</p>
                </div>
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-center">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">Inventive Step</span>
                  <p className="text-base font-extrabold text-emerald-700 mt-1">{result.inventive_step}</p>
                </div>
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-center">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">TK Risk Level</span>
                  <p className={`text-base font-extrabold mt-1 ${result.tk_risk === "HIGH" ? "text-rose-600" : "text-emerald-700"}`}>
                    {result.tk_risk}
                  </p>
                </div>
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-center">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">Biological Material Risk</span>
                  <p className={`text-base font-extrabold mt-1 ${result.biological_material_risk === "HIGH" ? "text-amber-600" : "text-emerald-700"}`}>
                    {result.biological_material_risk}
                  </p>
                </div>
              </div>

              {/* Exclusions */}
              {result.potential_exclusions && result.potential_exclusions.length > 0 && (
                <div className="p-4 rounded-xl bg-rose-50 border border-rose-200">
                  <h3 className="font-bold text-xs text-rose-900 mb-2 flex items-center gap-1.5">
                    <AlertTriangle size={15} className="text-rose-600" />
                    <span>Potential Exclusions Under Section 3 (Indian Patents Act 1970)</span>
                  </h3>
                  <ul className="space-y-1 text-xs text-rose-800">
                    {result.potential_exclusions.map((ex: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-1.5">
                        <span>•</span>
                        <span>{ex}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Relevant Provisions */}
              <div>
                <h3 className="font-bold text-xs text-slate-800 uppercase mb-2">Relevant Legal Provisions</h3>
                <div className="flex flex-wrap gap-2">
                  {result.relevant_provisions?.map((prov: string, idx: number) => (
                    <span key={idx} className="text-xs px-3 py-1 bg-slate-100 text-slate-800 rounded-lg font-semibold border border-slate-200">
                      {prov}
                    </span>
                  ))}
                </div>
              </div>

              {/* Next Steps */}
              <div>
                <h3 className="font-bold text-xs text-slate-800 uppercase mb-2">Recommended Next Actions</h3>
                <div className="space-y-2">
                  {result.recommended_next_steps?.map((step: string, idx: number) => (
                    <div key={idx} className="flex items-start gap-2.5 text-xs text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-100">
                      <CheckCircle size={15} className="text-emerald-600 flex-shrink-0 mt-0.5" />
                      <span>{step}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Disclaimer */}
            <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-800">
              ⚠️ <b>Disclaimer:</b> {result.disclaimer}
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
