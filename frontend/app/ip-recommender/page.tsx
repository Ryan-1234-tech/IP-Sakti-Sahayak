import { useState } from "react";
import AppShell from "@/components/layout/AppShell";
import { useJurisdiction } from "@/lib/jurisdiction";
import { Sparkles, ArrowRight, CheckCircle, AlertCircle, HelpCircle, Shield, FileText } from "lucide-react";

interface IPRecommendation {
  ip_type: string;
  relevant: boolean;
  status: string;
  why: string;
  potential_areas: string[];
}


export default function IPRecommenderPage() {
  const { jurisdiction } = useJurisdiction();
  const [description, setDescription] = useState(
    "I developed a new Ayurvedic formulation using turmeric, ashwagandha and neem in a unique ratio, created a custom bottle shape design, registered a brand name 'AyurZen', and drafted a product manual."
  );
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<IPRecommendation[] | null>(null);
  const [summary, setSummary] = useState("");

  const handleAssess = async () => {
    if (!description.trim()) return;
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/features/ip-recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description, jurisdiction: jurisdiction }),
      });
      const data = await res.json();
      setResults(data.recommendations || []);
      setSummary(data.summary || "");
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
        <div className="bg-gradient-to-r from-emerald-900 to-slate-900 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2.5 bg-emerald-600/40 rounded-xl border border-emerald-500/30">
              <Sparkles size={22} className="text-emerald-300" />
            </div>
            <div>
              <h1 className="font-bold text-xl text-white">Identify My IP — Multi-Category IP Protection Recommender</h1>
              <p className="text-xs text-slate-300">
                Describe your invention, product, brand, or content to identify all applicable IP protections under Indian law.
              </p>
            </div>
          </div>
        </div>

        {/* Input Card */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <label className="block text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">
            Describe Your Invention / Product / Brand / Literature
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
            className="w-full text-xs p-3.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 bg-slate-50 text-slate-900"
            placeholder="e.g. I developed a new herbal syrup for joint pain, designed a custom glass container, created a brand name 'JointHeal', and wrote an instruction brochure."
          />
          <div className="mt-3 flex justify-end">
            <button
              onClick={handleAssess}
              disabled={loading}
              className="flex items-center gap-2 px-6 py-2.5 bg-emerald-700 hover:bg-emerald-600 text-white font-bold text-xs rounded-xl shadow transition-all disabled:opacity-50"
            >
              {loading ? "Analyzing Description..." : "Identify Applicable IP Types"}
              <ArrowRight size={14} />
            </button>
          </div>
        </div>

        {/* Results */}
        {results && (
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-900 font-medium">
              ✨ <b>Summary:</b> {summary}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {results.map((rec, idx) => (
                <div
                  key={idx}
                  className={`bg-white rounded-2xl border p-5 flex flex-col justify-between shadow-sm transition-all ${
                    rec.relevant ? "border-emerald-500 ring-1 ring-emerald-500/20" : "border-slate-200 opacity-80"
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="font-bold text-sm text-slate-900">{rec.ip_type}</span>
                      <span
                        className={`text-[10px] px-2.5 py-0.5 rounded-full font-bold uppercase ${
                          rec.status === "Highly Relevant"
                            ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                            : rec.status === "Potentially Relevant"
                            ? "bg-blue-100 text-blue-800 border border-blue-300"
                            : "bg-amber-100 text-amber-800 border border-amber-300"
                        }`}
                      >
                        {rec.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed mb-4">{rec.why}</p>

                    {rec.potential_areas && rec.potential_areas.length > 0 && (
                      <div className="space-y-1">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Potential Scope:</span>
                        <div className="flex flex-wrap gap-1">
                          {rec.potential_areas.map((area, aIdx) => (
                            <span key={aIdx} className="text-[10px] px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-medium">
                              • {area}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
                    <span>Statutory Category</span>
                    <span className="font-semibold text-emerald-700">Preliminary Assessment</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-[11px] text-amber-800 leading-relaxed">
              ⚠️ <b>Statutory Notice:</b> This recommendation is a preliminary automated analysis based on text keyword patterns. Formal eligibility depends on full prior-art search and examination under Indian IP legislation.
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
