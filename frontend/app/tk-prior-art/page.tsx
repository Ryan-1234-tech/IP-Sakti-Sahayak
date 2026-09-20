"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import AppShell from "@/components/layout/AppShell";
import { useJurisdiction } from "@/lib/jurisdiction";
import {
  Search,
  BookOpen,
  ExternalLink,
  Sparkles,
  ArrowRight,
  ShieldAlert,
  Database,
  RefreshCw,
  FileSearch,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
} from "lucide-react";
import {
  TKPriorArtRequest,
  TKPriorArtResponse,
  searchTKPriorArt,
} from "@/lib/api";
import ConfidenceBadge from "@/components/ConfidenceBadge";
import SourceCard from "@/components/SourceCard";

const SAMPLE_SEARCHES = [
  {
    title: "Curcuma Wound Healing Synergy",
    formulation: "Curcuma longa rhizome extract with Piper nigrum bioavailability booster",
    ingredients: "Curcuma longa (Turmeric), Piper nigrum (Black Pepper)",
    traditional_use: "Vranaropana (wound healing) and Shothahara (anti-inflammatory) in classical Ayurveda",
    therapeutic_claim: "Accelerated dermal wound contraction and anti-inflammatory synergistic formulation",
    keywords: "curcumin, piperine, wound healing, bioavailability, topical formulation",
  },
  {
    title: "Ashwagandha Cognitive Stress Blend",
    formulation: "Withania somnifera and Bacopa monnieri aqueous extract tablet",
    ingredients: "Withania somnifera (Ashwagandha), Bacopa monnieri (Brahmi)",
    traditional_use: "Medhya Rasayana (memory & cognitive enhancer) in Charaka Samhita",
    therapeutic_claim: "Anxiolytic and neuroprotective synergistic composition for stress-induced cognitive impairment",
    keywords: "withanolides, bacosides, neuroprotection, anxiolytic, cognitive function",
  },
  {
    title: "Guduchi Antipyretic Decoction",
    formulation: "Tinospora cordifolia and Andrographis paniculata aqueous extract",
    ingredients: "Tinospora cordifolia (Giloy), Andrographis paniculata (Kalmegh)",
    traditional_use: "Jwarahara (antipyretic) in Bhavaprakasha and Siddha text",
    therapeutic_claim: "Broad-spectrum antipyretic and immunomodulatory decoction",
    keywords: "tinospora, andrographis, antipyretic, fever, immunostimulant",
  },
];

export default function TKPriorArtPage() {
  const router = useRouter();
  const { jurisdiction } = useJurisdiction();

  const [formulation, setFormulation] = useState(SAMPLE_SEARCHES[0].formulation);
  const [ingredients, setIngredients] = useState(SAMPLE_SEARCHES[0].ingredients);
  const [traditionalUse, setTraditionalUse] = useState(SAMPLE_SEARCHES[0].traditional_use);
  const [claim, setClaim] = useState(SAMPLE_SEARCHES[0].therapeutic_claim);
  const [keywords, setKeywords] = useState(SAMPLE_SEARCHES[0].keywords);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TKPriorArtResponse | null>(null);

  const handleLoadSample = (sample: typeof SAMPLE_SEARCHES[0]) => {
    setFormulation(sample.formulation);
    setIngredients(sample.ingredients);
    setTraditionalUse(sample.traditional_use);
    setClaim(sample.therapeutic_claim);
    setKeywords(sample.keywords);
    setResult(null);
  };

  const handleSearch = async () => {
    if (!formulation.trim() && !ingredients.trim()) {
      alert("Please provide at least a formulation description or botanical ingredients.");
      return;
    }
    setLoading(true);
    try {
      const payload: TKPriorArtRequest = {
        formulation: formulation,
        ingredients: ingredients,
        traditional_use: traditionalUse,
        therapeutic_claim: claim,
        keywords: keywords,
        jurisdiction: jurisdiction,
      };
      const res = await searchTKPriorArt(payload);
      setResult(res);
    } catch (e: any) {
      alert(`Prior art search error: ${e.message || e}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <div className="h-full overflow-y-auto bg-slate-50 p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header Banner */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[11px] font-bold uppercase tracking-wider">
                  Prior Art Discovery Aid
                </span>
                <span className="text-xs text-slate-400">|</span>
                <span className="text-xs font-semibold text-slate-500">
                  CSIR TKDL, IPO InPASS &amp; WIPO PATENTSCOPE Strategy
                </span>
              </div>
              <h1 className="text-2xl font-black text-slate-900 tracking-tight">
                Traditional Knowledge &amp; Prior-Art Discovery
              </h1>
              <p className="text-xs text-slate-500 mt-1 max-w-3xl">
                Explore potential prior-art references for botanical formulations and generate transparent search strategies with direct database pointers for CSIR TKDL, Indian Patent Office InPASS, and WIPO PATENTSCOPE.
              </p>
            </div>

            {/* Presets */}
            <div className="flex flex-wrap gap-2 items-center">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider w-full md:w-auto">Sample Queries:</span>
              {SAMPLE_SEARCHES.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => handleLoadSample(s)}
                  className="px-3 py-1.5 bg-slate-100 hover:bg-emerald-50 hover:text-emerald-800 border border-slate-200 hover:border-emerald-300 rounded-xl text-xs font-semibold text-slate-700 transition-all"
                >
                  {s.title}
                </button>
              ))}
            </div>
          </div>

          {/* Twin Column Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* ── LEFT PANEL: Search Input Form (6 Cols) ── */}
            <div className="lg:col-span-6 space-y-5">
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
                <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
                  <FileSearch size={18} className="text-emerald-700" />
                  <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                    Invention &amp; Prior-Art Query
                  </h3>
                </div>

                <div className="space-y-3.5 text-xs">
                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">
                      Formulation / Invention Concept *
                    </label>
                    <textarea
                      rows={2}
                      value={formulation}
                      onChange={(e) => setFormulation(e.target.value)}
                      className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:bg-white"
                      placeholder="Describe the product formulation, active ingredients, and extraction method..."
                    />
                  </div>

                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">
                      Botanical / Herbal Ingredients (with Latin Names)
                    </label>
                    <input
                      type="text"
                      value={ingredients}
                      onChange={(e) => setIngredients(e.target.value)}
                      className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:bg-white"
                      placeholder="e.g. Curcuma longa, Piper nigrum"
                    />
                  </div>

                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">
                      Known Classical / Traditional Medicinal Use
                    </label>
                    <input
                      type="text"
                      value={traditionalUse}
                      onChange={(e) => setTraditionalUse(e.target.value)}
                      className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:bg-white"
                      placeholder="e.g. Documented as Vranaropana (wound healing) in Ayurvedic Pharmacopoeia"
                    />
                  </div>

                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">
                      Specific Therapeutic Claim / Advantage
                    </label>
                    <input
                      type="text"
                      value={claim}
                      onChange={(e) => setClaim(e.target.value)}
                      className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:bg-white"
                      placeholder="e.g. Synergistic 3x enhancement in topical epithelial tissue regeneration"
                    />
                  </div>

                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">
                      Search Keywords &amp; IPC Technical Terms
                    </label>
                    <input
                      type="text"
                      value={keywords}
                      onChange={(e) => setKeywords(e.target.value)}
                      className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:bg-white"
                      placeholder="e.g. curcumin, piperine, synergistic ratio, wound healing, A61K 36/00"
                    />
                  </div>

                  <button
                    onClick={handleSearch}
                    disabled={loading}
                    className="w-full py-3.5 bg-emerald-700 hover:bg-emerald-600 disabled:bg-slate-300 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2 shadow-xs transition-all mt-2"
                  >
                    {loading ? <RefreshCw size={16} className="animate-spin" /> : <Search size={16} />}
                    <span>{loading ? "Searching Prior-Art Knowledge Base..." : "Search Prior-Art & Generate Registry Pointers"}</span>
                  </button>
                </div>
              </div>

              {/* Warning Card on Prior Art Scope */}
              <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 text-xs space-y-1.5 text-amber-900">
                <p className="font-bold flex items-center gap-1.5">
                  <AlertCircle size={15} className="text-amber-700" />
                  Honest Prior-Art Disclosure Note
                </p>
                <p className="text-[11px] text-amber-800 leading-relaxed">
                  No automated search tool can guarantee that &ldquo;No prior art exists.&rdquo; This tool provides a discovery aid and structured query strategies. Full clearance requires official searches across CSIR TKDL access facilities, InPASS, and a registered patent attorney opinion.
                </p>
              </div>
            </div>

            {/* ── RIGHT PANEL: Prior Art Results & Registry Pointers (6 Cols) ── */}
            <div className="lg:col-span-6 space-y-5">
              {result ? (
                <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden sticky top-6">
                  {/* Status Banner */}
                  <div className="p-6 bg-gradient-to-r from-emerald-950 via-slate-900 to-emerald-900 text-white">
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <span className="inline-flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                        <BookOpen size={12} />
                        Prior-Art Analysis (Step 7)
                      </span>
                      <ConfidenceBadge
                        confidence={result.confidence as any}
                        score={result.confidence_score}
                      />
                    </div>

                    <h2 className="text-xl font-black text-white mt-1 leading-tight">
                      Traditional Knowledge: {result.traditional_knowledge}
                    </h2>
                    <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                      {result.potential_prior_art}
                    </p>
                  </div>

                  <div className="p-6 space-y-4 text-xs">
                    {/* Database Pointers (Step 7 requirement) */}
                    <div>
                      <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                        <Database size={14} className="text-emerald-700" />
                        Authoritative Database Search Pointers ({result.database_pointers?.length || 0})
                      </h4>
                      <div className="space-y-2.5">
                        {result.database_pointers?.map((p, idx) => (
                          <div key={idx} className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5 text-[11px]">
                            <div className="flex items-center justify-between">
                              <span className="font-bold text-slate-900 text-xs">{p.database_name}</span>
                              <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px]">
                                {p.access_type}
                              </span>
                            </div>

                            <p className="text-slate-700">
                              <strong className="text-slate-900">Recommended Strategy: </strong>
                              {p.recommended_search_strategy}
                            </p>

                            <p className="text-slate-500 italic text-[10px]">
                              <strong>Access Note: </strong>{p.access_note}
                            </p>

                            {p.search_url && (
                              <a
                                href={p.search_url}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 hover:text-emerald-900 hover:underline pt-1"
                              >
                                <span>Open Official Portal</span>
                                <ExternalLink size={12} />
                              </a>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Next Steps */}
                    <div className="p-3.5 bg-emerald-50/70 border border-emerald-200 rounded-xl space-y-1">
                      <p className="font-bold text-emerald-900 flex items-center gap-1.5">
                        <CheckCircle2 size={14} className="text-emerald-700" />
                        Recommended Next Step
                      </p>
                      <p className="text-emerald-950 leading-relaxed text-[11px]">
                        {result.next_step}
                      </p>
                    </div>

                    {/* Cited Evidence Sources */}
                    {result.sources && result.sources.length > 0 && (
                      <div className="pt-2 border-t border-slate-100">
                        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">
                          Retrieved Evidence Sources ({result.sources.length})
                        </h4>
                        <div className="grid grid-cols-1 gap-2">
                          {result.sources.map((s, idx) => (
                            <SourceCard key={idx} source={s} index={idx + 1} />
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Legal Disclaimer */}
                    <p className="text-[11px] text-slate-400 italic pt-2 text-center">
                      ⚖️ {result.disclaimer}
                    </p>

                    {/* Ask AI Trigger */}
                    <button
                      onClick={() =>
                        router.push(
                          `/chat?prompt=${encodeURIComponent(
                            `I am preparing a patent search for '${formulation}'. Based on the prior art guidance, how do I structure my patent claim language to demonstrate non-obvious synergistic efficacy over TKDL prior art?`
                          )}`
                        )
                      }
                      className="w-full py-2.5 bg-emerald-900 hover:bg-emerald-800 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2 transition-colors shadow-xs"
                    >
                      <Sparkles size={14} className="text-emerald-400" />
                      <span>Ask AI Advisor for Synergistic Claim Drafting</span>
                      <ArrowRight size={14} />
                    </button>
                  </div>
                </div>
              ) : (
                <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-3">
                  <Search size={36} className="mx-auto text-emerald-600/40" />
                  <h3 className="text-sm font-bold text-slate-800">Ready for Prior-Art Search</h3>
                  <p className="text-xs text-slate-500 max-w-md mx-auto">
                    Provide your formulation or ingredients on the left and click <strong>Search Prior-Art &amp; Generate Registry Pointers</strong> to retrieve evidence and official search strategies.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
