"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import AppShell from "@/components/layout/AppShell";
import { useJurisdiction } from "@/lib/jurisdiction";
import {
  Leaf,
  BookOpen,
  Plus,
  Trash2,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Search,
  RefreshCw,
  FlaskConical,
  Scale,
  Layers,
  ShieldCheck,
  Building2,
  HelpCircle,
  ExternalLink,
} from "lucide-react";
import {
  IngredientInput,
  TKRiskRequest,
  TKRiskResponse,
  AYUSHClassifyRequest,
  AYUSHClassifyResponse,
  assessTKRisk,
  classifyAYUSH,
} from "@/lib/api";
import ConfidenceBadge from "@/components/ConfidenceBadge";
import SourceCard from "@/components/SourceCard";

const SYSTEMS = ["Ayurveda", "Siddha", "Unani", "Sowa-Rigpa", "Polyherbal", "Homeopathy"];
const CLASSICAL_TEXTS = [
  "Ayurvedic Pharmacopoeia of India (API)",
  "Charaka Samhita",
  "Sushruta Samhita",
  "Ashtanga Hridaya",
  "Bhavaprakasha",
  "Siddha Formulary of India (SFI)",
  "National Formulary of Unani Medicine (NFUM)",
  "None / Proprietary R&D",
];

const SAMPLE_CLASSIFICATION_PRESETS = [
  {
    title: "Classical Chyawanprash",
    name: "Classical Chyawanprash Formulation",
    system: "Ayurveda",
    source: "Classical Ayurvedic Text",
    text: "Ayurvedic Pharmacopoeia of India (API)",
    claims: "Rasayana rejuvenation, immunity support, anti-aging as described in Charaka Samhita.",
    isBio: true,
    isNovel: false,
    ingredients: [
      { name: "Amalaki", latin_name: "Phyllanthus emblica", percentage: 50 },
      { name: "Guduchi", latin_name: "Tinospora cordifolia", percentage: 20 },
      { name: "Pippali", latin_name: "Piper longum", percentage: 10 },
      { name: "Dashamoola", latin_name: "Ten Roots Classical Compound", percentage: 20 },
    ],
  },
  {
    title: "Proprietary Anti-Diabetic Capsule",
    name: "GlycoShield Proprietary Herbal Capsule",
    system: "Ayurveda",
    source: "Proprietary / In-House Innovation",
    text: "None / Proprietary R&D",
    claims: "Synergistic glucose metabolism regulator with patented extraction ratio.",
    isBio: true,
    isNovel: false,
    ingredients: [
      { name: "Meshashringi (Gymnema)", latin_name: "Gymnema sylvestre", percentage: 40 },
      { name: "Vijaysar", latin_name: "Pterocarpus marsupium", percentage: 35 },
      { name: "Jamun Seed Extract", latin_name: "Syzygium cumini", percentage: 25 },
    ],
  },
  {
    title: "Phytopharmaceutical Fraction",
    name: "Purified Withanolide-A Standardized Bioactive Fraction",
    system: "Polyherbal",
    source: "Standardized Purified Fraction (>65%)",
    text: "None / Proprietary R&D",
    claims: "Neuroprotective treatment for cognitive decline supported by Phase I/II clinical trials.",
    isBio: true,
    isNovel: true,
    ingredients: [
      { name: "Standardized Withanolide-A Fraction (98% HPLC purity)", latin_name: "Withania somnifera", percentage: 100, is_novel: true },
    ],
  },
  {
    title: "Ayurveda-Aahar Herbal Tea",
    name: "Daily Prana Golden Turmeric Elixir Tea",
    system: "Ayurveda",
    source: "Traditional Food Recipe / Dietary",
    text: "Bhavaprakasha",
    claims: "Nutritional dietary supplement for daily vitality and metabolic balance.",
    isBio: true,
    isNovel: false,
    ingredients: [
      { name: "Haridra (Turmeric powder)", latin_name: "Curcuma longa", percentage: 50 },
      { name: "Twak (Cinnamon)", latin_name: "Cinnamomum verum", percentage: 30 },
      { name: "Shunthi (Dry Ginger)", latin_name: "Zingiber officinale", percentage: 20 },
    ],
  },
];

export default function TKRiskPage() {
  const router = useRouter();
  const { jurisdiction } = useJurisdiction();

  // Active Tab: "classify" (Step 5) | "tk_risk" (Section 3p audit)
  const [activeTab, setActiveTab] = useState<"classify" | "tk_risk">("classify");

  // ============================================================
  // Tab 1: Guided AYUSH Formulation Classification State (Step 5)
  // ============================================================
  const [cFormName, setCFormName] = useState(SAMPLE_CLASSIFICATION_PRESETS[0].name);
  const [cSystem, setCSystem] = useState(SAMPLE_CLASSIFICATION_PRESETS[0].system);
  const [cSource, setCSource] = useState(SAMPLE_CLASSIFICATION_PRESETS[0].source);
  const [cText, setCText] = useState(SAMPLE_CLASSIFICATION_PRESETS[0].text);
  const [cClaims, setCClaims] = useState(SAMPLE_CLASSIFICATION_PRESETS[0].claims);
  const [cIsBio, setCIsBio] = useState(SAMPLE_CLASSIFICATION_PRESETS[0].isBio);
  const [cIngredients, setCIngredients] = useState<IngredientInput[]>(SAMPLE_CLASSIFICATION_PRESETS[0].ingredients);
  const [cCommercial, setCCommercial] = useState(true);

  const [newCIngName, setNewCIngName] = useState("");
  const [newCIngLatin, setNewCIngLatin] = useState("");
  const [newCIngPercent, setNewCIngPercent] = useState("");
  const [newCIngNovel, setNewCIngNovel] = useState(false);

  const [isClassifying, setIsClassifying] = useState(false);
  const [classifyResult, setClassifyResult] = useState<AYUSHClassifyResponse | null>(null);

  // ============================================================
  // Tab 2: Section 3(p) TK Risk State
  // ============================================================
  const [riskFormName, setRiskFormName] = useState("Ashwagandha & Guduchi Immunity Elixir");
  const [riskSystem, setRiskSystem] = useState("Ayurveda");
  const [riskClaims, setRiskClaims] = useState("Boosts natural immunity and reduces stress.");
  const [riskIngredients, setRiskIngredients] = useState<IngredientInput[]>([
    { name: "Ashwagandha", latin_name: "Withania somnifera", percentage: 50 },
    { name: "Guduchi / Giloy", latin_name: "Tinospora cordifolia", percentage: 50 },
  ]);

  const [newHerbName, setNewHerbName] = useState("");
  const [newHerbLatin, setNewHerbLatin] = useState("");
  const [newHerbPercent, setNewHerbPercent] = useState("");

  const [isAssessingRisk, setIsAssessingRisk] = useState(false);
  const [riskResult, setRiskResult] = useState<TKRiskResponse | null>(null);

  // Preset Load
  const handleLoadClassifyPreset = (preset: typeof SAMPLE_CLASSIFICATION_PRESETS[0]) => {
    setCFormName(preset.name);
    setCSystem(preset.system);
    setCSource(preset.source);
    setCText(preset.text);
    setCClaims(preset.claims);
    setCIsBio(preset.isBio);
    setCIngredients(preset.ingredients);
    setClassifyResult(null);
  };

  // Add Herb to Classification List
  const handleAddClassifyHerb = () => {
    if (!newCIngName.trim()) return;
    setCIngredients((prev) => [
      ...prev,
      {
        name: newCIngName.trim(),
        latin_name: newCIngLatin.trim() || undefined,
        percentage: newCIngPercent ? parseFloat(newCIngPercent) : undefined,
        is_novel: newCIngNovel,
      },
    ]);
    setNewCIngName("");
    setNewCIngLatin("");
    setNewCIngPercent("");
    setNewCIngNovel(false);
  };

  const handleRemoveClassifyHerb = (index: number) => {
    setCIngredients((prev) => prev.filter((_, i) => i !== index));
  };

  // Run Step 5 Guided Classification
  const handleRunClassification = async () => {
    if (!cFormName.trim()) {
      alert("Please provide a formulation name.");
      return;
    }
    setIsClassifying(true);
    try {
      const payload: AYUSHClassifyRequest = {
        formulation_name: cFormName,
        formulation_source: cSource,
        authoritative_classical_text: cText,
        ingredients: cIngredients,
        novel_ingredients: cIngredients.filter((i) => i.is_novel).map((i) => i.name),
        biological_materials_used: cIsBio,
        therapeutic_claims: cClaims,
        system: cSystem,
        commercialization_intent: cCommercial,
        jurisdiction: jurisdiction,
      };
      const res = await classifyAYUSH(payload);
      setClassifyResult(res);
    } catch (e: any) {
      alert(`Classification error: ${e.message || e}`);
    } finally {
      setIsClassifying(false);
    }
  };

  // Run Section 3(p) Risk Assessment
  const handleRunRiskAssessment = async () => {
    if (!riskFormName.trim() || riskIngredients.length === 0) {
      alert("Please provide a formulation name and at least one ingredient.");
      return;
    }
    setIsAssessingRisk(true);
    try {
      const payload: TKRiskRequest = {
        formulation_name: riskFormName,
        system: riskSystem,
        ingredients: riskIngredients,
        proposed_claims: riskClaims,
        jurisdiction: jurisdiction,
      };
      const res = await assessTKRisk(payload);
      setRiskResult(res);
    } catch (e: any) {
      alert(`Assessment error: ${e.message || e}`);
    } finally {
      setIsAssessingRisk(false);
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
                  AYUSH Regulatory &amp; IP Engine
                </span>
                <span className="text-xs text-slate-400">|</span>
                <span className="text-xs font-semibold text-slate-500">
                  {jurisdiction === "INDIA" ? "🇮🇳 Indian Legal Framework" : "🌐 International Framework"}
                </span>
              </div>
              <h1 className="text-2xl font-black text-slate-900 tracking-tight">
                AYUSH Formulation Classifier &amp; TKDL Risk Assessor
              </h1>
              <p className="text-xs text-slate-500 mt-1 max-w-3xl">
                Perform official statutory categorization across 7 AYUSH drug classes (Classical, P&amp;P, Phytopharmaceutical, Ayurveda-Aahar, etc.) and audit Section 3(p) Traditional Knowledge patentability risks.
              </p>
            </div>

            {/* Mode Tab Switcher */}
            <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200">
              <button
                type="button"
                onClick={() => setActiveTab("classify")}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                  activeTab === "classify"
                    ? "bg-emerald-700 text-white shadow-xs"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                <Layers size={15} />
                <span>1. Guided AYUSH Classification</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("tk_risk")}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                  activeTab === "tk_risk"
                    ? "bg-emerald-700 text-white shadow-xs"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                <Scale size={15} />
                <span>2. Section 3(p) TKDL Risk Audit</span>
              </button>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* TAB 1: GUIDED AYUSH FORMULATION CLASSIFICATION (STEP 5)                   */}
          {/* ========================================================================= */}
          {activeTab === "classify" && (
            <div className="space-y-6">
              {/* Presets Row */}
              <div className="flex items-center gap-2 flex-wrap bg-white p-3 rounded-xl border border-slate-200">
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Quick Presets:</span>
                {SAMPLE_CLASSIFICATION_PRESETS.map((p, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleLoadClassifyPreset(p)}
                    className="px-3 py-1 bg-slate-100 hover:bg-emerald-50 hover:text-emerald-800 border border-slate-200 hover:border-emerald-300 rounded-lg text-xs font-semibold text-slate-700 transition-all"
                  >
                    {p.title}
                  </button>
                ))}
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* ── LEFT PANEL: Guided Classification Form (6 Cols) ── */}
                <div className="lg:col-span-6 space-y-5">
                  <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
                    <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
                      <FlaskConical size={18} className="text-emerald-700" />
                      <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                        Formulation &amp; Regulatory Parameters
                      </h3>
                    </div>

                    <div className="space-y-3.5 text-xs">
                      <div>
                        <label className="block font-semibold text-slate-700 mb-1">Product / Formulation Name *</label>
                        <input
                          type="text"
                          value={cFormName}
                          onChange={(e) => setCFormName(e.target.value)}
                          className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:bg-white"
                          placeholder="e.g. Classical Chyawanprash or Proprietary Synergy Capsule"
                        />
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div>
                          <label className="block font-semibold text-slate-700 mb-1">Traditional System</label>
                          <select
                            value={cSystem}
                            onChange={(e) => setCSystem(e.target.value)}
                            className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600"
                          >
                            {SYSTEMS.map((s) => (
                              <option key={s} value={s}>{s}</option>
                            ))}
                          </select>
                        </div>

                        <div>
                          <label className="block font-semibold text-slate-700 mb-1">Classical Text Reference</label>
                          <select
                            value={cText}
                            onChange={(e) => setCText(e.target.value)}
                            className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600"
                          >
                            {CLASSICAL_TEXTS.map((t) => (
                              <option key={t} value={t}>{t}</option>
                            ))}
                          </select>
                        </div>
                      </div>

                      <div>
                        <label className="block font-semibold text-slate-700 mb-1">Therapeutic Claims &amp; Intended Use</label>
                        <textarea
                          rows={2}
                          value={cClaims}
                          onChange={(e) => setCClaims(e.target.value)}
                          className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:bg-white"
                          placeholder="Describe intended health benefits, clinical rationale, or indications..."
                        />
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                        <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-700 bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                          <input
                            type="checkbox"
                            checked={cIsBio}
                            onChange={(e) => setCIsBio(e.target.checked)}
                            className="w-4 h-4 text-emerald-600 rounded"
                          />
                          <span>Uses Biological / Botanical Resources</span>
                        </label>

                        <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-700 bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                          <input
                            type="checkbox"
                            checked={cCommercial}
                            onChange={(e) => setCCommercial(e.target.checked)}
                            className="w-4 h-4 text-emerald-600 rounded"
                          />
                          <span>Commercial Manufacturing Intent</span>
                        </label>
                      </div>
                    </div>

                    {/* Ingredients Builder */}
                    <div className="space-y-3 pt-2 border-t border-slate-100">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                          Formulation Ingredients ({cIngredients.length})
                        </span>
                      </div>

                      <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-xs">
                          <input
                            type="text"
                            value={newCIngName}
                            onChange={(e) => setNewCIngName(e.target.value)}
                            placeholder="Ingredient name (e.g. Ashwagandha)"
                            className="px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-600"
                          />
                          <input
                            type="text"
                            value={newCIngLatin}
                            onChange={(e) => setNewCIngLatin(e.target.value)}
                            placeholder="Botanical / Latin name"
                            className="px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-600"
                          />
                          <div className="flex gap-2">
                            <input
                              type="number"
                              value={newCIngPercent}
                              onChange={(e) => setNewCIngPercent(e.target.value)}
                              placeholder="% (e.g. 50)"
                              className="w-full px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-600"
                            />
                            <button
                              type="button"
                              onClick={handleAddClassifyHerb}
                              className="px-3 py-1.5 bg-emerald-700 hover:bg-emerald-600 text-white font-bold text-xs rounded-lg flex items-center gap-1 shadow-xs transition-colors flex-shrink-0"
                            >
                              <Plus size={14} />
                              <span>Add</span>
                            </button>
                          </div>
                        </div>

                        <label className="flex items-center gap-2 cursor-pointer text-[11px] font-medium text-slate-600">
                          <input
                            type="checkbox"
                            checked={newCIngNovel}
                            onChange={(e) => setNewCIngNovel(e.target.checked)}
                            className="w-3.5 h-3.5 text-emerald-600 rounded"
                          />
                          <span>Standardized / Purified Novel Active Fraction (&gt;65% purity)</span>
                        </label>
                      </div>

                      {/* Ingredients list */}
                      <div className="space-y-1.5 max-h-48 overflow-y-auto">
                        {cIngredients.map((ing, idx) => (
                          <div
                            key={idx}
                            className="p-2.5 bg-white border border-slate-200 rounded-lg flex items-center justify-between text-xs hover:border-emerald-300 transition-colors"
                          >
                            <div className="flex items-center gap-2">
                              <span className="w-5 h-5 rounded bg-emerald-100 text-emerald-800 font-bold flex items-center justify-center text-[10px]">
                                {idx + 1}
                              </span>
                              <div>
                                <span className="font-bold text-slate-900">{ing.name}</span>
                                {ing.latin_name && <span className="text-slate-500 italic ml-1.5 text-[11px]">({ing.latin_name})</span>}
                                {ing.is_novel && (
                                  <span className="ml-2 px-1.5 py-0.2 bg-purple-100 text-purple-800 text-[10px] font-bold rounded">
                                    Novel Fraction
                                  </span>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              {ing.percentage && (
                                <span className="font-mono text-slate-700 font-bold text-[11px]">{ing.percentage}%</span>
                              )}
                              <button
                                onClick={() => handleRemoveClassifyHerb(idx)}
                                className="p-1 text-slate-400 hover:text-rose-600 transition-colors"
                              >
                                <Trash2 size={14} />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <button
                      onClick={handleRunClassification}
                      disabled={isClassifying}
                      className="w-full py-3 bg-emerald-700 hover:bg-emerald-600 disabled:bg-slate-300 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2 shadow-xs transition-all mt-3"
                    >
                      {isClassifying ? <RefreshCw size={16} className="animate-spin" /> : <Layers size={16} />}
                      <span>{isClassifying ? "Evaluating Statutory AYUSH Classification..." : "Classify AYUSH Formulation & IP Path"}</span>
                    </button>
                  </div>
                </div>

                {/* ── RIGHT PANEL: 7-Branch Classification Result (6 Cols) ── */}
                <div className="lg:col-span-6 space-y-5">
                  {classifyResult ? (
                    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden sticky top-6">
                      {/* Classification Badge Header */}
                      <div className="p-6 bg-gradient-to-r from-emerald-950 via-slate-900 to-emerald-900 text-white">
                        <div className="flex items-start justify-between gap-3 mb-2">
                          <span className="inline-flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                            <ShieldCheck size={12} />
                            Statutory Classification (Step 5)
                          </span>
                          <ConfidenceBadge
                            confidence={classifyResult.confidence as any}
                            score={classifyResult.confidence_score}
                          />
                        </div>

                        <h2 className="text-xl font-black text-white mt-1 leading-tight">
                          {classifyResult.product_classification}
                        </h2>
                        <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                          {classifyResult.basis}
                        </p>
                      </div>

                      {/* Structured Result Breakdown */}
                      <div className="p-6 space-y-4 text-xs">
                        {/* Summary Matrix Cards */}
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
                          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
                            <span className="text-[10px] font-bold text-slate-400 uppercase block">Traditional Knowledge</span>
                            <span className="font-extrabold text-xs text-slate-900 mt-1 block">
                              {classifyResult.traditional_knowledge}
                            </span>
                          </div>

                          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
                            <span className="text-[10px] font-bold text-slate-400 uppercase block">Biological Resource</span>
                            <span className="font-extrabold text-xs text-slate-900 mt-1 block">
                              {classifyResult.biological_resource}
                            </span>
                          </div>

                          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
                            <span className="text-[10px] font-bold text-slate-400 uppercase block">ABS Review</span>
                            <span className="font-extrabold text-xs text-emerald-700 mt-1 block">
                              {classifyResult.abs}
                            </span>
                          </div>

                          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
                            <span className="text-[10px] font-bold text-slate-400 uppercase block">TKDL Prior Art</span>
                            <span className="font-extrabold text-xs text-indigo-700 mt-1 block">
                              {classifyResult.tkdl_prior_art}
                            </span>
                          </div>
                        </div>

                        {/* Regulatory Considerations */}
                        <div className="p-3.5 bg-emerald-50/70 border border-emerald-200 rounded-xl space-y-1">
                          <p className="font-bold text-emerald-900 flex items-center gap-1.5">
                            <Building2 size={14} className="text-emerald-700" />
                            Regulatory &amp; Licensing Considerations
                          </p>
                          <p className="text-emerald-800 leading-relaxed text-[11px]">
                            {classifyResult.regulatory_considerations}
                          </p>
                        </div>

                        {/* IP Implications */}
                        <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                          <p className="font-bold text-slate-900 flex items-center gap-1.5">
                            <Scale size={14} className="text-indigo-700" />
                            Intellectual Property &amp; Patentability Implications
                          </p>
                          <p className="text-slate-700 leading-relaxed text-[11px]">
                            {classifyResult.ip_implications}
                          </p>
                        </div>

                        {/* Next Steps List */}
                        <div>
                          <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">
                            Statutory Action Steps
                          </h4>
                          <div className="space-y-1.5">
                            {classifyResult.next_steps.map((st, i) => (
                              <div key={i} className="flex items-start gap-2 bg-slate-50 p-2.5 rounded-lg border border-slate-100 text-[11px]">
                                <span className="font-bold text-emerald-700">{i + 1}.</span>
                                <span className="text-slate-700">{st}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Sources */}
                        {classifyResult.sources && classifyResult.sources.length > 0 && (
                          <div className="pt-2 border-t border-slate-100">
                            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">
                              Authoritative Sources Cited ({classifyResult.sources.length})
                            </h4>
                            <div className="grid grid-cols-1 gap-2">
                              {classifyResult.sources.map((s, idx) => (
                                <SourceCard key={idx} source={s} index={idx + 1} />
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Disclaimer */}
                        <p className="text-[11px] text-slate-400 italic pt-2 text-center">
                          ⚖️ {classifyResult.disclaimer}
                        </p>

                        {/* Ask AI Trigger */}
                        <button
                          onClick={() =>
                            router.push(
                              `/chat?prompt=${encodeURIComponent(
                                `My product '${cFormName}' was classified as '${classifyResult.product_classification}'. How should I structure my manufacturing license application and patent claims under Indian law?`
                              )}`
                            )
                          }
                          className="w-full py-2.5 bg-emerald-900 hover:bg-emerald-800 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2 transition-colors shadow-xs"
                        >
                          <Sparkles size={14} className="text-emerald-400" />
                          <span>Ask AI Advisor for Licensing &amp; Drafting Strategy</span>
                          <ArrowRight size={14} />
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-3">
                      <Layers size={36} className="mx-auto text-emerald-600/40" />
                      <h3 className="text-sm font-bold text-slate-800">Ready for Classification</h3>
                      <p className="text-xs text-slate-500 max-w-md mx-auto">
                        Fill in formulation details on the left or select a preset, then click <strong>Classify AYUSH Formulation</strong> to determine official regulatory path and Section 3(p) implications.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* ========================================================================= */}
          {/* TAB 2: SECTION 3(p) TKDL RISK AUDIT                                       */}
          {/* ========================================================================= */}
          {activeTab === "tk_risk" && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Left Panel */}
              <div className="lg:col-span-6 space-y-5">
                <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
                  <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
                    <Scale size={18} className="text-emerald-700" />
                    <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                      Section 3(p) Prior-Art Audit Parameters
                    </h3>
                  </div>

                  <div className="space-y-3.5 text-xs">
                    <div>
                      <label className="block font-semibold text-slate-700 mb-1">Formulation Name *</label>
                      <input
                        type="text"
                        value={riskFormName}
                        onChange={(e) => setRiskFormName(e.target.value)}
                        className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:bg-white"
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <label className="block font-semibold text-slate-700 mb-1">Traditional System</label>
                        <select
                          value={riskSystem}
                          onChange={(e) => setRiskSystem(e.target.value)}
                          className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600"
                        >
                          {SYSTEMS.map((s) => (
                            <option key={s} value={s}>{s}</option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <label className="block font-semibold text-slate-700 mb-1">Proposed Intended Claims</label>
                        <input
                          type="text"
                          value={riskClaims}
                          onChange={(e) => setRiskClaims(e.target.value)}
                          className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:bg-white"
                        />
                      </div>
                    </div>

                    {/* Herb List */}
                    <div className="space-y-2 pt-2 border-t border-slate-100">
                      <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                        Botanical Ingredients ({riskIngredients.length})
                      </span>

                      <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                          <input
                            type="text"
                            value={newHerbName}
                            onChange={(e) => setNewHerbName(e.target.value)}
                            placeholder="Herb name (e.g. Tulsi)"
                            className="px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg text-xs"
                          />
                          <input
                            type="text"
                            value={newHerbLatin}
                            onChange={(e) => setNewHerbLatin(e.target.value)}
                            placeholder="Latin name"
                            className="px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg text-xs"
                          />
                          <div className="flex gap-2">
                            <input
                              type="number"
                              value={newHerbPercent}
                              onChange={(e) => setNewHerbPercent(e.target.value)}
                              placeholder="%"
                              className="w-full px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg text-xs"
                            />
                            <button
                              type="button"
                              onClick={() => {
                                if (!newHerbName.trim()) return;
                                setRiskIngredients((prev) => [
                                  ...prev,
                                  {
                                    name: newHerbName.trim(),
                                    latin_name: newHerbLatin.trim() || undefined,
                                    percentage: newHerbPercent ? parseFloat(newHerbPercent) : undefined,
                                  },
                                ]);
                                setNewHerbName("");
                                setNewHerbLatin("");
                                setNewHerbPercent("");
                              }}
                              className="px-3 py-1.5 bg-emerald-700 text-white font-bold text-xs rounded-lg flex-shrink-0"
                            >
                              <Plus size={14} />
                            </button>
                          </div>
                        </div>
                      </div>

                      <div className="space-y-1.5 max-h-48 overflow-y-auto">
                        {riskIngredients.map((ing, idx) => (
                          <div
                            key={idx}
                            className="p-2.5 bg-white border border-slate-200 rounded-lg flex items-center justify-between text-xs"
                          >
                            <div>
                              <span className="font-bold text-slate-900">{ing.name}</span>
                              {ing.latin_name && <span className="text-slate-500 italic ml-1 text-[11px]">({ing.latin_name})</span>}
                            </div>
                            <div className="flex items-center gap-2">
                              {ing.percentage && <span className="font-mono text-slate-700 font-bold">{ing.percentage}%</span>}
                              <button
                                onClick={() => setRiskIngredients((prev) => prev.filter((_, i) => i !== idx))}
                                className="p-1 text-slate-400 hover:text-rose-600"
                              >
                                <Trash2 size={14} />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <button
                      onClick={handleRunRiskAssessment}
                      disabled={isAssessingRisk}
                      className="w-full py-3 bg-emerald-700 hover:bg-emerald-600 disabled:bg-slate-300 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2 shadow-xs transition-all mt-3"
                    >
                      {isAssessingRisk ? <RefreshCw size={16} className="animate-spin" /> : <Search size={16} />}
                      <span>{isAssessingRisk ? "Cross-referencing TKDL & Classical Records..." : "Audit Section 3(p) Patent Risk"}</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* Right Panel: TK Risk Result */}
              <div className="lg:col-span-6 space-y-5">
                {riskResult ? (
                  <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden sticky top-6">
                    <div
                      className={`p-6 text-white ${
                        riskResult.risk_level === "HIGH_RISK"
                          ? "bg-gradient-to-r from-rose-950 via-rose-900 to-rose-950"
                          : riskResult.risk_level === "MODERATE_RISK"
                          ? "bg-gradient-to-r from-amber-950 via-amber-900 to-amber-950"
                          : "bg-gradient-to-r from-emerald-950 via-emerald-900 to-emerald-950"
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <span className="inline-flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-white/10 text-white border border-white/20">
                            Section 3(p) Audit
                          </span>
                          <h2 className="text-xl font-black text-white mt-1 leading-tight">{riskResult.formulation_name}</h2>
                          <p className="text-xs text-white/80">{riskResult.system} Formulation</p>
                        </div>

                        <div className="w-14 h-14 rounded-2xl bg-white/10 border border-white/20 flex flex-col items-center justify-center">
                          <span className="text-xl font-black leading-none">{riskResult.overall_risk_score}</span>
                          <span className="text-[8px] font-bold uppercase opacity-80 mt-0.5">Risk</span>
                        </div>
                      </div>

                      <div className="pt-2 border-t border-white/10 flex items-center justify-between text-xs">
                        <span className="text-white/80">Compliance Status:</span>
                        <span className="font-bold">{riskResult.section_3p_compliance_status}</span>
                      </div>
                    </div>

                    <div className="p-6 space-y-4 text-xs">
                      <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                        <p className="font-bold text-slate-900">Patentability Assessment</p>
                        <p className="text-slate-600 leading-relaxed text-[11px]">{riskResult.patentability_assessment}</p>
                      </div>

                      <div>
                        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">
                          Matched TKDL &amp; Classical Prior Art ({riskResult.matched_entries.length})
                        </h4>
                        <div className="space-y-2">
                          {riskResult.matched_entries.length === 0 ? (
                            <div className="p-3 border border-emerald-200 bg-emerald-50/50 rounded-xl text-[11px] text-emerald-900 font-semibold flex items-center gap-2">
                              <CheckCircle2 size={14} className="text-emerald-600" />
                              <span>No direct classical text conflicts detected for these herbs!</span>
                            </div>
                          ) : (
                            riskResult.matched_entries.map((m, idx) => (
                              <div key={idx} className="p-3 bg-white border border-slate-200 rounded-xl space-y-1.5 text-[11px]">
                                <div className="flex items-center justify-between">
                                  <span className="font-bold text-slate-900">{m.traditional_name} ({m.latin_name})</span>
                                  <span className="px-1.5 py-0.2 bg-rose-100 text-rose-800 font-bold rounded text-[10px]">
                                    {m.risk_factor}
                                  </span>
                                </div>
                                <div className="grid grid-cols-2 gap-2 text-slate-600 pt-1 border-t border-slate-100">
                                  <div>
                                    <span className="text-slate-400">Classical Source: </span>
                                    <span className="font-semibold text-slate-700">{m.classical_text_source}</span>
                                  </div>
                                  <div>
                                    <span className="text-slate-400">TKDL Ref: </span>
                                    <span className="font-mono text-emerald-700 font-bold">{m.tkdl_reference}</span>
                                  </div>
                                </div>
                                <p className="text-slate-600 pt-1">
                                  <strong>Documented Traditional Use:</strong> {m.known_therapeutic_use}
                                </p>
                              </div>
                            ))
                          )}
                        </div>
                      </div>

                      <div>
                        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">Key Recommendations</h4>
                        <ul className="space-y-1.5">
                          {riskResult.key_recommendations.map((rec, idx) => (
                            <li key={idx} className="flex items-start gap-2 bg-emerald-50/60 p-2.5 rounded-lg border border-emerald-200 text-[11px] text-slate-800">
                              <Sparkles size={14} className="text-emerald-600 flex-shrink-0 mt-0.5" />
                              <span>{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      <p className="text-[11px] text-slate-400 italic pt-2 text-center">
                        ⚖️ Information provided for guidance only, not legal advice.
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-3">
                    <BookOpen size={36} className="mx-auto text-emerald-600/40" />
                    <h3 className="text-sm font-bold text-slate-800">Ready for TKDL Audit</h3>
                    <p className="text-xs text-slate-500 max-w-md mx-auto">
                      Specify ingredients on the left and click <strong>Audit Section 3(p) Patent Risk</strong> to cross-reference classical treatises and TKDL indices.
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
