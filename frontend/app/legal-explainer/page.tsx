import { useState } from "react";
import AppShell from "@/components/layout/AppShell";
import { useJurisdiction } from "@/lib/jurisdiction";
import { MessageSquare, Search, BookOpen, CheckCircle, ArrowRight, Shield } from "lucide-react";

export default function LegalExplainerPage() {
  const { jurisdiction } = useJurisdiction();
  const [legalQuery, setLegalQuery] = useState("Section 3(p)");
  const [searchQuery, setSearchQuery] = useState("Ayurvedic topical hydrogel turmeric ashwagandha formulation novelty");
  const [explainResult, setExplainResult] = useState<any>(null);
  const [priorArtResult, setPriorArtResult] = useState<any>(null);
  const [loadingExplain, setLoadingExplain] = useState(false);
  const [loadingSearch, setLoadingSearch] = useState(false);

  const handleExplain = async () => {
    if (!legalQuery) return;
    setLoadingExplain(true);
    try {
      const res = await fetch("http://localhost:8000/api/features/legal-explain", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: legalQuery, jurisdiction: jurisdiction }),
      });
      const data = await res.json();
      setExplainResult(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingExplain(false);
    }
  };

  const handleSearchPriorArt = async () => {
    if (!searchQuery) return;
    setLoadingSearch(true);
    try {
      const res = await fetch("http://localhost:8000/api/features/prior-art-search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery, top_k: 4, jurisdiction: jurisdiction }),
      });
      const data = await res.json();
      setPriorArtResult(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingSearch(false);
    }
  };

  return (
    <AppShell>
      <div className="h-full overflow-y-auto p-8 max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="bg-gradient-to-r from-emerald-950 via-slate-900 to-emerald-900 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2.5 bg-emerald-600/40 rounded-xl border border-emerald-500/30">
              <BookOpen size={22} className="text-emerald-300" />
            </div>
            <div>
              <h1 className="font-bold text-xl text-white">Legal Language Explainer &amp; Prior-Art Search</h1>
              <p className="text-xs text-slate-300">
                Lookup plain English explanations for complex statutory sections (e.g. Section 3(p), Section 3(d), Section 6 BDA) and perform FAISS vector similarity search across indexed gazettes.
              </p>
            </div>
          </div>
        </div>

        {/* Section 1: Legal Language Explainer */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <h2 className="font-bold text-xs uppercase tracking-wider text-slate-800 flex items-center gap-2 border-b border-slate-100 pb-2">
            <MessageSquare size={16} className="text-emerald-700" />
            <span>Plain English Legal Provision Explainer</span>
          </h2>

          <div className="flex gap-3">
            <input
              type="text"
              value={legalQuery}
              onChange={(e) => setLegalQuery(e.target.value)}
              placeholder="e.g. Section 3(p), Section 3(d), Section 6 Biological Diversity Act"
              className="flex-1 text-xs p-3 rounded-xl border border-slate-300 bg-slate-50 text-slate-900 font-bold"
            />
            <button
              onClick={handleExplain}
              disabled={loadingExplain}
              className="px-6 py-3 bg-emerald-700 hover:bg-emerald-600 text-white font-bold text-xs rounded-xl shadow transition-all disabled:opacity-50"
            >
              {loadingExplain ? "Explaining..." : "Explain Provision"}
            </button>
          </div>

          <div className="flex flex-wrap gap-2 text-[11px] text-slate-500">
            <span className="font-bold">Quick Examples:</span>
            {["Section 3(p)", "Section 3(d)", "Section 3(e)", "Section 6 BDA"].map((ex) => (
              <button
                key={ex}
                onClick={() => {
                  setLegalQuery(ex);
                }}
                className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-semibold border border-slate-200"
              >
                {ex}
              </button>
            ))}
          </div>

          {explainResult && (
            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-3 mt-4">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-sm text-slate-900">{explainResult.provision_name}</h3>
                <span className="text-[10px] font-bold px-2.5 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-300">
                  {explainResult.source_document}
                </span>
              </div>

              <div>
                <span className="text-[10px] font-bold uppercase text-slate-400">Plain English Meaning:</span>
                <p className="text-xs text-slate-800 font-medium leading-relaxed mt-0.5">{explainResult.plain_english_explanation}</p>
              </div>

              <div>
                <span className="text-[10px] font-bold uppercase text-slate-400">Why It Matters:</span>
                <p className="text-xs text-emerald-900 font-medium leading-relaxed mt-0.5">{explainResult.why_it_matters}</p>
              </div>

              <div>
                <span className="text-[10px] font-bold uppercase text-slate-400">Practical Example:</span>
                <p className="text-xs text-slate-700 bg-white p-3 rounded-xl border border-slate-200 mt-0.5 italic">
                  "{explainResult.practical_example}"
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Section 2: Prior-Art Vector Similarity Search */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <h2 className="font-bold text-xs uppercase tracking-wider text-slate-800 flex items-center gap-2 border-b border-slate-100 pb-2">
            <Search size={16} className="text-emerald-700" />
            <span>Prior-Art &amp; Document Similarity Search</span>
          </h2>

          <div className="flex gap-3">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Enter technical invention keywords or claims..."
              className="flex-1 text-xs p-3 rounded-xl border border-slate-300 bg-slate-50 text-slate-900 font-medium"
            />
            <button
              onClick={handleSearchPriorArt}
              disabled={loadingSearch}
              className="px-6 py-3 bg-emerald-700 hover:bg-emerald-600 text-white font-bold text-xs rounded-xl shadow transition-all disabled:opacity-50"
            >
              {loadingSearch ? "Searching Vector Store..." : "Search Prior-Art"}
            </button>
          </div>

          {priorArtResult && (
            <div className="space-y-4 mt-4">
              <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-900 font-medium">
                ℹ️ {priorArtResult.summary_disclaimer}
              </div>

              <div className="space-y-3">
                {priorArtResult.results?.map((res: any, idx: number) => (
                  <div key={idx} className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2">
                    <div className="flex items-center justify-between">
                      <h4 className="font-bold text-xs text-slate-900">{res.document_title}</h4>
                      <span className="text-xs font-extrabold px-2.5 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-300">
                        {res.similarity_score}% Similarity
                      </span>
                    </div>

                    <p className="text-xs text-slate-700 bg-white p-3 rounded-lg border border-slate-200 leading-relaxed font-mono">
                      "{res.relevant_passage}"
                    </p>

                    <div className="flex items-center justify-between text-[11px] text-slate-500">
                      <span>Doc Type: <b>{res.document_type}</b></span>
                      <span className="font-semibold text-emerald-800">• {res.why_relevant}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
