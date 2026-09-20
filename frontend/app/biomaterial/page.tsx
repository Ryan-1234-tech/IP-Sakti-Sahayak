"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import AppShell from "@/components/layout/AppShell";
import { useJurisdiction } from "@/lib/jurisdiction";
import {
  UploadCloud,
  CheckCircle,
  AlertTriangle,
  ArrowRight,
  BookOpen,
  Shield,
  Leaf,
  Building,
  Scale,
  RefreshCw,
  Sparkles,
  Info,
  DollarSign,
  FileCheck,
} from "lucide-react";
import {
  ABSAssessRequest,
  ABSAssessResponse,
  assessABS,
} from "@/lib/api";
import ConfidenceBadge from "@/components/ConfidenceBadge";
import SourceCard from "@/components/SourceCard";

const SAMPLE_ABS_PRESETS = [
  {
    title: "Indian MSME Patenting Herbal Extract",
    resource: "Curcuma longa (Turmeric) & Withania somnifera (Ashwagandha)",
    location: "Western Ghats, Kerala & Madhya Pradesh",
    origin: "India",
    isIndianOrigin: true,
    tk: true,
    entity: "Indian MSME / Startup (100% Indian Shareholding)",
    use: "Commercial IP / Patent Filing in India",
    commercial: true,
  },
  {
    title: "Foreign MNC Researching Indian Bio-Resource",
    resource: "Bacopa monnieri (Brahmi)",
    location: "Wetlands of West Bengal, India",
    origin: "India",
    isIndianOrigin: true,
    tk: true,
    entity: "Foreign Corporation / Non-Resident Indian (Section 3 Entity)",
    use: "Commercial Utilization & Global Patenting",
    commercial: true,
  },
  {
    title: "Indian Academic Pure Non-Commercial Research",
    resource: "Rauvolfia serpentina (Sarpagandha)",
    location: "Dehradun Forest Reserve",
    origin: "India",
    isIndianOrigin: true,
    tk: false,
    entity: "Indian Public University / Academic Institute",
    use: "Non-Commercial Academic Research",
    commercial: false,
  },
];

export default function BioMaterialPage() {
  const router = useRouter();
  const { jurisdiction } = useJurisdiction();

  // Form Questionnaire State
  const [usesBio, setUsesBio] = useState(true);
  const [resourceName, setResourceName] = useState(SAMPLE_ABS_PRESETS[0].resource);
  const [sourceLocation, setSourceLocation] = useState(SAMPLE_ABS_PRESETS[0].location);
  const [geoOrigin, setGeoOrigin] = useState(SAMPLE_ABS_PRESETS[0].origin);
  const [isIndianOrigin, setIsIndianOrigin] = useState(true);
  const [associatedTk, setAssociatedTk] = useState(true);
  const [userEntity, setUserEntity] = useState(SAMPLE_ABS_PRESETS[0].entity);
  const [intendedUse, setIntendedUse] = useState(SAMPLE_ABS_PRESETS[0].use);
  const [commercialIntent, setCommercialIntent] = useState(true);

  // Result state
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ABSAssessResponse | null>(null);

  const handleLoadPreset = (preset: typeof SAMPLE_ABS_PRESETS[0]) => {
    setResourceName(preset.resource);
    setSourceLocation(preset.location);
    setGeoOrigin(preset.origin);
    setIsIndianOrigin(preset.isIndianOrigin);
    setAssociatedTk(preset.tk);
    setUserEntity(preset.entity);
    setIntendedUse(preset.use);
    setCommercialIntent(preset.commercial);
    setResult(null);
  };

  const handleRunAssessment = async () => {
    setLoading(true);
    try {
      const payload: ABSAssessRequest = {
        biological_resource_used: usesBio,
        resource_name: resourceName,
        source_location: sourceLocation,
        is_indian_origin: isIndianOrigin,
        geographical_origin: geoOrigin,
        traditional_knowledge_associated: associatedTk,
        intended_use: intendedUse,
        commercialization_intent: commercialIntent,
        user_entity_type: userEntity,
        jurisdiction: jurisdiction,
      };
      const res = await assessABS(payload);
      setResult(res);
    } catch (err: any) {
      alert(`ABS assessment error: ${err.message || err}`);
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
                  Biodiversity Compliance Engine
                </span>
                <span className="text-xs text-slate-400">|</span>
                <span className="text-xs font-semibold text-slate-500">
                  Biological Diversity Act 2002 / 2023 &amp; Nagoya Protocol
                </span>
              </div>
              <h1 className="text-2xl font-black text-slate-900 tracking-tight">
                Biological Resource &amp; ABS Assessor
              </h1>
              <p className="text-xs text-slate-500 mt-1 max-w-3xl">
                Evaluate mandatory National Biodiversity Authority (NBA, Chennai) Form III prior approvals, Section 3 entity restrictions, State Biodiversity Board (SBB) intimations, and statutory Access &amp; Benefit Sharing (ABS) rates.
              </p>
            </div>

            {/* Presets */}
            <div className="flex flex-wrap gap-2 items-center">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider w-full md:w-auto">Sample Presets:</span>
              {SAMPLE_ABS_PRESETS.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => handleLoadPreset(p)}
                  className="px-3 py-1.5 bg-slate-100 hover:bg-emerald-50 hover:text-emerald-800 border border-slate-200 hover:border-emerald-300 rounded-xl text-xs font-semibold text-slate-700 transition-all"
                >
                  {p.title.split(" ")[0]} {p.title.split(" ")[1]}
                </button>
              ))}
            </div>
          </div>

          {/* Twin Column Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* ── LEFT PANEL: ABS Questionnaire Form (6 Cols) ── */}
            <div className="lg:col-span-6 space-y-5">
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
                <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
                  <Leaf size={18} className="text-emerald-700" />
                  <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                    Biological Resource Questionnaire
                  </h3>
                </div>

                <div className="space-y-4 text-xs">
                  {/* Biological Material Toggle */}
                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">
                      Does your invention/product use a biological resource? *
                    </label>
                    <select
                      value={usesBio ? "yes" : "no"}
                      onChange={(e) => setUsesBio(e.target.value === "yes")}
                      className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-600"
                    >
                      <option value="yes">YES — Uses botanical, fungal, microbial, or plant genetic material</option>
                      <option value="no">NO — 100% synthetic chemical / non-biological only</option>
                    </select>
                  </div>

                  {/* Resource Name */}
                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">
                      Biological Resource Name / Species *
                    </label>
                    <input
                      type="text"
                      value={resourceName}
                      onChange={(e) => setResourceName(e.target.value)}
                      className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:bg-white"
                      placeholder="e.g. Curcuma longa, Withania somnifera"
                    />
                  </div>

                  {/* Location & Origin */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                      <label className="block font-semibold text-slate-700 mb-1">Source / Harvesting Location</label>
                      <input
                        type="text"
                        value={sourceLocation}
                        onChange={(e) => setSourceLocation(e.target.value)}
                        className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600"
                        placeholder="e.g. Western Ghats, Kerala"
                      />
                    </div>

                    <div>
                      <label className="block font-semibold text-slate-700 mb-1">Geographical Origin</label>
                      <input
                        type="text"
                        value={geoOrigin}
                        onChange={(e) => setGeoOrigin(e.target.value)}
                        className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600"
                        placeholder="e.g. India"
                      />
                    </div>
                  </div>

                  {/* Entity Type Selector */}
                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">
                      Applicant Entity Type (Section 3 vs Section 7 Determination) *
                    </label>
                    <select
                      value={userEntity}
                      onChange={(e) => setUserEntity(e.target.value)}
                      className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-600"
                    >
                      <option value="Indian MSME / Startup (100% Indian Shareholding)">
                        Indian MSME / Startup / Individual Citizen (100% Indian Capital)
                      </option>
                      <option value="Foreign Corporation / Non-Resident Indian (Section 3 Entity)">
                        Foreign Entity / NRI / Indian Company with Foreign Equity or Management (Section 3)
                      </option>
                      <option value="Indian Public University / Academic Institute">
                        Indian Public University / Non-Commercial Research Body
                      </option>
                    </select>
                  </div>

                  {/* Intended Use */}
                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">
                      Intended Commercial or Research Activity *
                    </label>
                    <select
                      value={intendedUse}
                      onChange={(e) => setIntendedUse(e.target.value)}
                      className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-600"
                    >
                      <option value="Commercial IP / Patent Filing in India">
                        Patent Application in India (Requires Section 6 / Form III Approval)
                      </option>
                      <option value="Commercial Utilization & Global Patenting">
                        Commercial Utilization, Manufacturing &amp; Global Patent Filing
                      </option>
                      <option value="Transfer of Research Results Outside India">
                        Transfer of Research Results to Non-Indian Entities (Section 4 / Form IV)
                      </option>
                      <option value="Non-Commercial Academic Research">
                        Pure Non-Commercial Academic Research in India
                      </option>
                    </select>
                  </div>

                  {/* Checkbox Triggers */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1 border-t border-slate-100">
                    <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-700 bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                      <input
                        type="checkbox"
                        checked={isIndianOrigin}
                        onChange={(e) => setIsIndianOrigin(e.target.checked)}
                        className="w-4 h-4 text-emerald-600 rounded"
                      />
                      <span>Bio-Resource Obtained from India</span>
                    </label>

                    <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-700 bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                      <input
                        type="checkbox"
                        checked={associatedTk}
                        onChange={(e) => setAssociatedTk(e.target.checked)}
                        className="w-4 h-4 text-emerald-600 rounded"
                      />
                      <span>Associated Traditional Knowledge Involved</span>
                    </label>
                  </div>

                  <button
                    onClick={handleRunAssessment}
                    disabled={loading}
                    className="w-full py-3.5 bg-emerald-700 hover:bg-emerald-600 disabled:bg-slate-300 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2 shadow-xs transition-all mt-2"
                  >
                    {loading ? <RefreshCw size={16} className="animate-spin" /> : <FileCheck size={16} />}
                    <span>{loading ? "Cross-referencing Biological Diversity Act 2002/2023..." : "Assess NBA & ABS Statutory Requirements"}</span>
                  </button>
                </div>
              </div>
            </div>

            {/* ── RIGHT PANEL: Statutory ABS Compliance Output (6 Cols) ── */}
            <div className="lg:col-span-6 space-y-5">
              {result ? (
                <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden sticky top-6">
                  {/* Status Banner */}
                  <div className="p-6 bg-gradient-to-r from-emerald-950 via-slate-900 to-emerald-900 text-white">
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <span className="inline-flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                        <Scale size={12} />
                        BDA 2002/2023 Statutory Review
                      </span>
                      <ConfidenceBadge
                        confidence={result.confidence as any}
                        score={result.confidence_score}
                      />
                    </div>

                    <h2 className="text-xl font-black text-white mt-1 leading-tight">
                      ABS Review: {result.abs_review}
                    </h2>
                    <p className="text-xs text-slate-300 mt-1 leading-relaxed font-mono">
                      {result.relevant_framework}
                    </p>
                  </div>

                  <div className="p-6 space-y-4 text-xs">
                    {/* Status Matrix */}
                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
                        <span className="text-[10px] font-bold text-slate-400 uppercase block">Biological Resource</span>
                        <span className="font-extrabold text-xs text-emerald-700 mt-1 block">
                          {result.biological_resource}
                        </span>
                      </div>

                      <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
                        <span className="text-[10px] font-bold text-slate-400 uppercase block">Traditional Knowledge</span>
                        <span className="font-extrabold text-xs text-slate-900 mt-1 block">
                          {result.traditional_knowledge}
                        </span>
                      </div>
                    </div>

                    {/* Statutory Actions Checklist */}
                    <div>
                      <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">
                        Statutory Approval Steps &amp; Form Filings
                      </h4>
                      <div className="space-y-2">
                        {result.next_steps.map((st, i) => (
                          <div key={i} className="flex items-start gap-2.5 bg-emerald-50/70 p-3 rounded-xl border border-emerald-200 text-emerald-950 text-[11px]">
                            <CheckCircle size={15} className="text-emerald-700 flex-shrink-0 mt-0.5" />
                            <span className="leading-relaxed font-medium">{st}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Cited Legal Sources */}
                    {result.sources && result.sources.length > 0 && (
                      <div className="pt-2 border-t border-slate-100">
                        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">
                          Authoritative Legal Sources ({result.sources.length})
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
                            `My biological resource '${resourceName}' requires NBA Form III clearance under Section 6 of Biological Diversity Act 2002. What is the step-by-step submission procedure and how does it coordinate with the Indian Patent Office?`
                          )}`
                        )
                      }
                      className="w-full py-2.5 bg-emerald-900 hover:bg-emerald-800 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2 transition-colors shadow-xs"
                    >
                      <Sparkles size={14} className="text-emerald-400" />
                      <span>Ask AI Advisor on NBA Form III Filing Workflow</span>
                      <ArrowRight size={14} />
                    </button>
                  </div>
                </div>
              ) : (
                <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-3">
                  <UploadCloud size={36} className="mx-auto text-emerald-600/40" />
                  <h3 className="text-sm font-bold text-slate-800">Ready for ABS Assessment</h3>
                  <p className="text-xs text-slate-500 max-w-md mx-auto">
                    Fill out the biological resource origin and entity type questionnaire on the left to verify Form I / Form III NBA statutory filing obligations.
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
