"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import AppShell from "@/components/layout/AppShell";
import {
  Building2,
  ShieldCheck,
  Award,
  Plus,
  Trash2,
  Save,
  CheckCircle2,
  AlertTriangle,
  AlertOctagon,
  Sparkles,
  ArrowRight,
  FileCheck,
  RefreshCw,
  Scale,
  Calendar,
  Layers,
} from "lucide-react";
import {
  BusinessProfile,
  CompliancePassport,
  IPAsset,
  createProfile,
  getProfiles,
  updateProfile,
  getCompliancePassport,
} from "@/lib/api";

const SECTORS = ["AYUSH", "Pharma & Healthcare", "Biotech", "Software & DeepTech", "Manufacturing / MSME", "Agriculture"];
const COMPANY_TYPES = ["Startup", "MSME", "Enterprise", "Researcher / Academic"];
const ASSET_TYPES = ["Patent", "Trademark", "GI", "Copyright"];
const STATUSES = ["Granted", "Pending", "Draft", "Expired"];

export default function PassportPage() {
  const router = useRouter();

  // Profile Form State
  const [profileId, setProfileId] = useState<string | null>(null);
  const [companyName, setCompanyName] = useState("AyurVeda BioTech Pvt Ltd");
  const [sector, setSector] = useState("AYUSH");
  const [companyType, setCompanyType] = useState("Startup");
  const [registrationNumber, setRegistrationNumber] = useState("UDYAM-KR-03-0012345");
  const [state, setState] = useState("Karnataka");
  const [ipAssets, setIpAssets] = useState<IPAsset[]>([
    { asset_type: "Patent", title: "Standardized Ashwagandha Extraction Process", status: "Granted", registration_no: "IN-2023-381920" },
    { asset_type: "Trademark", title: "AyurShield Herbals (Class 5)", status: "Granted", registration_no: "TM-5928191" },
    { asset_type: "GI", title: "Coorg Herbal Geographic Origin Certification", status: "Pending" },
  ]);

  // Asset Form State
  const [newAssetType, setNewAssetType] = useState("Patent");
  const [newAssetTitle, setNewAssetTitle] = useState("");
  const [newAssetStatus, setNewAssetStatus] = useState("Granted");
  const [newAssetRegNo, setNewAssetRegNo] = useState("");

  // UI state
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [passport, setPassport] = useState<CompliancePassport | null>(null);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState("");

  // Load existing profile or fetch latest
  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      try {
        const profiles = await getProfiles();
        if (profiles.length > 0) {
          const active = profiles[0];
          setProfileId(active.id || null);
          setCompanyName(active.company_name);
          setSector(active.sector);
          setCompanyType(active.company_type);
          setRegistrationNumber(active.registration_number || "");
          setState(active.state || "");
          setIpAssets(active.ip_assets || []);

          if (active.id) {
            const pass = await getCompliancePassport(active.id);
            setPassport(pass);
          }
        } else {
          // Create initial default demo profile
          const created = await createProfile({
            company_name: companyName,
            sector: sector,
            company_type: companyType,
            registration_number: registrationNumber,
            state: state,
            ip_assets: ipAssets,
          });
          if (created.id) {
            setProfileId(created.id);
            const pass = await getCompliancePassport(created.id);
            setPassport(pass);
          }
        }
      } catch (err) {
        console.error("Failed to load profile/passport:", err);
      } finally {
        setIsLoading(false);
      }
    }

    loadData();
  }, []);

  // Save profile and re-fetch passport
  const handleSaveProfile = async () => {
    setIsSaving(true);
    setSaveSuccessMsg("");
    try {
      let activeId = profileId;
      const payload: BusinessProfile = {
        company_name: companyName,
        sector: sector,
        company_type: companyType,
        registration_number: registrationNumber,
        state: state,
        ip_assets: ipAssets,
      };

      if (activeId) {
        await updateProfile(activeId, payload);
      } else {
        const created = await createProfile(payload);
        activeId = created.id || null;
        setProfileId(activeId);
      }

      if (activeId) {
        const updatedPass = await getCompliancePassport(activeId);
        setPassport(updatedPass);
        setSaveSuccessMsg("Business profile & passport updated successfully!");
        setTimeout(() => setSaveSuccessMsg(""), 3500);
      }
    } catch (err: any) {
      alert(`Error saving profile: ${err.message || err}`);
    } finally {
      setIsSaving(false);
    }
  };

  // Add new IP Asset to state
  const handleAddAsset = () => {
    if (!newAssetTitle.trim()) return;
    const newAsset: IPAsset = {
      asset_type: newAssetType,
      title: newAssetTitle.trim(),
      status: newAssetStatus,
      registration_no: newAssetRegNo.trim() || undefined,
    };
    setIpAssets((prev) => [...prev, newAsset]);
    setNewAssetTitle("");
    setNewAssetRegNo("");
  };

  // Remove IP Asset from state
  const handleRemoveAsset = (index: number) => {
    setIpAssets((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <AppShell>
      <div className="h-full overflow-y-auto bg-slate-50 p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header Banner */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[11px] font-bold uppercase tracking-wider">
                  Compliance Twin Engine
                </span>
                <span className="text-xs text-slate-400">|</span>
                <span className="text-xs font-semibold text-slate-500">Live Statutory Audit</span>
              </div>
              <h1 className="text-2xl font-black text-slate-900 tracking-tight">Business Profile &amp; IP Passport</h1>
              <p className="text-xs text-slate-500 mt-1 max-w-2xl">
                Manage your enterprise details and IP portfolio on the left. The dynamic Compliance Passport on the right automatically computes your legal health score and audit readiness.
              </p>
            </div>

            <button
              onClick={handleSaveProfile}
              disabled={isSaving}
              className="px-5 py-3 bg-emerald-700 hover:bg-emerald-600 disabled:bg-slate-300 text-white font-bold text-sm rounded-xl flex items-center gap-2 shadow-sm transition-all self-start md:self-auto"
            >
              {isSaving ? <RefreshCw size={16} className="animate-spin" /> : <Save size={16} />}
              <span>{isSaving ? "Re-computing..." : "Save & Re-calculate Passport"}</span>
            </button>
          </div>

          {saveSuccessMsg && (
            <div className="p-3.5 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold rounded-xl flex items-center gap-2 animate-fade-up">
              <CheckCircle2 size={16} className="text-emerald-600" />
              <span>{saveSuccessMsg}</span>
            </div>
          )}

          {/* ── TwinPage Split Panel Layout ── */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* ── LEFT PANEL: Business Profile & IP Assets Form (7 Cols) ── */}
            <div className="lg:col-span-7 space-y-6">
              {/* Company Profile Details Card */}
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-5">
                <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
                  <Building2 size={18} className="text-emerald-700" />
                  <h3 className="text-base font-bold text-slate-900">Company Information</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div className="md:col-span-2">
                    <label className="block font-semibold text-slate-700 mb-1">Company / Entity Name *</label>
                    <input
                      type="text"
                      value={companyName}
                      onChange={(e) => setCompanyName(e.target.value)}
                      className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:bg-white"
                      placeholder="e.g. AyurVeda BioTech Pvt Ltd"
                    />
                  </div>

                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">Industry Sector</label>
                    <select
                      value={sector}
                      onChange={(e) => setSector(e.target.value)}
                      className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:bg-white"
                    >
                      {SECTORS.map((s) => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">Entity Classification</label>
                    <select
                      value={companyType}
                      onChange={(e) => setCompanyType(e.target.value)}
                      className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:bg-white"
                    >
                      {COMPANY_TYPES.map((t) => (
                        <option key={t} value={t}>{t}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">Udyam / CIN / Registration No.</label>
                    <input
                      type="text"
                      value={registrationNumber}
                      onChange={(e) => setRegistrationNumber(e.target.value)}
                      className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:bg-white"
                      placeholder="e.g. UDYAM-KR-03-0012345"
                    />
                  </div>

                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">State / Jurisdiction</label>
                    <input
                      type="text"
                      value={state}
                      onChange={(e) => setState(e.target.value)}
                      className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:bg-white"
                      placeholder="e.g. Karnataka"
                    />
                  </div>
                </div>
              </div>

              {/* IP Asset Portfolio Editor Card */}
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-5">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <Layers size={18} className="text-emerald-700" />
                    <h3 className="text-base font-bold text-slate-900">IP Assets Portfolio</h3>
                  </div>
                  <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                    {ipAssets.length} Assets Registered
                  </span>
                </div>

                {/* Add New Asset Controls */}
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
                  <p className="text-xs font-bold text-slate-800">Add IP Asset (Patent / Trademark / GI / Copyright)</p>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-2.5 text-xs">
                    <div>
                      <select
                        value={newAssetType}
                        onChange={(e) => setNewAssetType(e.target.value)}
                        className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-600"
                      >
                        {ASSET_TYPES.map((t) => (
                          <option key={t} value={t}>{t}</option>
                        ))}
                      </select>
                    </div>

                    <div className="md:col-span-2">
                      <input
                        type="text"
                        value={newAssetTitle}
                        onChange={(e) => setNewAssetTitle(e.target.value)}
                        placeholder="Asset title or brand name *"
                        className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-600"
                      />
                    </div>

                    <div>
                      <select
                        value={newAssetStatus}
                        onChange={(e) => setNewAssetStatus(e.target.value)}
                        className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-600"
                      >
                        {STATUSES.map((st) => (
                          <option key={st} value={st}>{st}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      value={newAssetRegNo}
                      onChange={(e) => setNewAssetRegNo(e.target.value)}
                      placeholder="Optional Patent/TM Registration Number (e.g. IN-2024-001)"
                      className="flex-1 px-3 py-2 bg-white border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-emerald-600"
                    />
                    <button
                      type="button"
                      onClick={handleAddAsset}
                      className="px-4 py-2 bg-emerald-700 hover:bg-emerald-600 text-white font-bold text-xs rounded-lg flex items-center gap-1 shadow-xs transition-colors"
                    >
                      <Plus size={14} />
                      <span>Add Asset</span>
                    </button>
                  </div>
                </div>

                {/* List of Asset Cards */}
                <div className="space-y-2.5">
                  {ipAssets.length === 0 ? (
                    <div className="text-center py-8 border-2 border-dashed border-slate-200 rounded-xl text-slate-400 text-xs">
                      No IP assets logged yet. Use the form above to add your patents or trademarks.
                    </div>
                  ) : (
                    ipAssets.map((asset, index) => (
                      <div
                        key={index}
                        className="p-3.5 bg-white border border-slate-200 rounded-xl flex items-center justify-between gap-3 hover:border-emerald-300 transition-colors shadow-2xs"
                      >
                        <div className="flex items-center gap-3 min-w-0">
                          <span
                            className={`px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider ${
                              asset.asset_type === "Patent"
                                ? "bg-amber-100 text-amber-900 border border-amber-300"
                                : asset.asset_type === "Trademark"
                                ? "bg-blue-100 text-blue-900 border border-blue-300"
                                : asset.asset_type === "GI"
                                ? "bg-emerald-100 text-emerald-900 border border-emerald-300"
                                : "bg-purple-100 text-purple-900 border border-purple-300"
                            }`}
                          >
                            {asset.asset_type}
                          </span>

                          <div className="min-w-0">
                            <p className="text-xs font-bold text-slate-900 truncate">{asset.title}</p>
                            <div className="flex items-center gap-2 text-[11px] text-slate-500">
                              <span>Status: <strong className="text-slate-700">{asset.status}</strong></span>
                              {asset.registration_no && (
                                <>
                                  <span>•</span>
                                  <span className="font-mono text-slate-600">{asset.registration_no}</span>
                                </>
                              )}
                            </div>
                          </div>
                        </div>

                        <button
                          type="button"
                          onClick={() => handleRemoveAsset(index)}
                          className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                          title="Remove asset"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>

            {/* ── RIGHT PANEL: Computed IP Compliance Passport Summary (5 Cols) ── */}
            <div className="lg:col-span-5 space-y-6">
              {passport ? (
                <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden sticky top-6">
                  {/* Passport Card Header with Gradient */}
                  <div className="bg-gradient-to-r from-[#0c1911] via-[#142e20] to-[#0c1911] p-6 text-white relative">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <span className="inline-flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-emerald-400 bg-emerald-950/80 border border-emerald-800/80 px-2.5 py-1 rounded-full">
                          <Award size={12} />
                          Official IP Passport
                        </span>
                        <h2 className="text-xl font-black text-white mt-2 leading-tight">{passport.company_name}</h2>
                        <p className="text-xs text-emerald-300/80 font-medium">{passport.sector} Sector • {passport.company_type}</p>
                      </div>

                      {/* Overall Compliance Score Badge */}
                      <div className="text-right flex flex-col items-end">
                        <div
                          className={`w-16 h-16 rounded-2xl flex flex-col items-center justify-center border-2 shadow-lg ${
                            passport.status_level === "EXCELLENT"
                              ? "bg-emerald-600 border-emerald-400 text-white"
                              : passport.status_level === "GOOD"
                              ? "bg-teal-600 border-teal-400 text-white"
                              : passport.status_level === "NEEDS_ATTENTION"
                              ? "bg-amber-600 border-amber-400 text-white"
                              : "bg-rose-600 border-rose-400 text-white"
                          }`}
                        >
                          <span className="text-2xl font-black leading-none">{passport.overall_score}</span>
                          <span className="text-[9px] font-bold opacity-80 uppercase tracking-tighter mt-0.5">Score</span>
                        </div>
                      </div>
                    </div>

                    {/* Status Level Badge */}
                    <div className="flex items-center justify-between pt-3 border-t border-white/10 text-xs">
                      <span className="text-slate-300">Compliance Level:</span>
                      <span
                        className={`font-black uppercase tracking-wide px-2.5 py-0.5 rounded text-[11px] ${
                          passport.status_level === "EXCELLENT"
                            ? "bg-emerald-500/30 text-emerald-300 border border-emerald-400/50"
                            : passport.status_level === "GOOD"
                            ? "bg-teal-500/30 text-teal-300 border border-teal-400/50"
                            : passport.status_level === "NEEDS_ATTENTION"
                            ? "bg-amber-500/30 text-amber-300 border border-amber-400/50"
                            : "bg-rose-500/30 text-rose-300 border border-rose-400/50"
                        }`}
                      >
                        {passport.status_level.replace("_", " ")}
                      </span>
                    </div>
                  </div>

                  {/* Body Content */}
                  <div className="p-6 space-y-5">
                    {/* Next Filing Deadline */}
                    {passport.next_filing_deadline && (
                      <div className="p-3 bg-amber-50/80 border border-amber-200 rounded-xl flex items-center gap-2.5 text-xs text-amber-900 font-semibold">
                        <Calendar size={16} className="text-amber-600 flex-shrink-0" />
                        <span>{passport.next_filing_deadline}</span>
                      </div>
                    )}

                    {/* Asset Portfolio Breakdown Pills */}
                    <div>
                      <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2.5">Asset Portfolio Count</h4>
                      <div className="grid grid-cols-4 gap-2 text-center">
                        <div className="p-2.5 bg-amber-50 border border-amber-200 rounded-xl">
                          <p className="text-lg font-black text-amber-900">{passport.asset_breakdown.patents_count}</p>
                          <p className="text-[10px] font-bold text-amber-700">Patents</p>
                        </div>
                        <div className="p-2.5 bg-blue-50 border border-blue-200 rounded-xl">
                          <p className="text-lg font-black text-blue-900">{passport.asset_breakdown.trademarks_count}</p>
                          <p className="text-[10px] font-bold text-blue-700">Trademarks</p>
                        </div>
                        <div className="p-2.5 bg-purple-50 border border-purple-200 rounded-xl">
                          <p className="text-lg font-black text-purple-900">{passport.asset_breakdown.copyrights_count}</p>
                          <p className="text-[10px] font-bold text-purple-700">Copyrights</p>
                        </div>
                        <div className="p-2.5 bg-emerald-50 border border-emerald-200 rounded-xl">
                          <p className="text-lg font-black text-emerald-900">{passport.asset_breakdown.gis_count}</p>
                          <p className="text-[10px] font-bold text-emerald-700">GIs</p>
                        </div>
                      </div>
                    </div>

                    {/* Interactive Compliance Audit Checklist */}
                    <div>
                      <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2.5">Statutory Audit Checklist</h4>
                      <div className="space-y-2.5">
                        {passport.compliance_checklist.map((chk, idx) => (
                          <div key={idx} className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1 text-xs">
                            <div className="flex items-center justify-between gap-2">
                              <span className="font-bold text-slate-900">{chk.item}</span>
                              <span
                                className={`px-2 py-0.5 rounded text-[10px] font-bold flex items-center gap-1 ${
                                  chk.status === "PASSED"
                                    ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                                    : chk.status === "WARNING"
                                    ? "bg-amber-100 text-amber-900 border border-amber-300"
                                    : "bg-rose-100 text-rose-900 border border-rose-300"
                                }`}
                              >
                                {chk.status === "PASSED" ? (
                                  <CheckCircle2 size={12} />
                                ) : chk.status === "WARNING" ? (
                                  <AlertTriangle size={12} />
                                ) : (
                                  <AlertOctagon size={12} />
                                )}
                                <span>{chk.status}</span>
                              </span>
                            </div>
                            <p className="text-slate-600 leading-relaxed text-[11px]">{chk.guidance}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Actionable Recommended Next Steps */}
                    <div>
                      <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2.5">Recommended Action Plan</h4>
                      <ul className="space-y-2 text-xs">
                        {passport.recommended_actions.map((act, idx) => (
                          <li key={idx} className="flex items-start gap-2 text-slate-700 bg-emerald-50/50 p-2.5 rounded-lg border border-emerald-100">
                            <Sparkles size={14} className="text-emerald-600 flex-shrink-0 mt-0.5" />
                            <span>{act}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Ask AI Advisor Button */}
                    <button
                      onClick={() =>
                        router.push(
                          `/chat?prompt=${encodeURIComponent(
                            `My company is ${passport.company_name} in the ${passport.sector} sector with compliance score ${passport.overall_score}/100. How can I resolve my compliance warnings and file patents/trademarks?`
                          )}`
                        )
                      }
                      className="w-full py-3 bg-emerald-900 hover:bg-emerald-800 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2 transition-colors shadow-xs"
                    >
                      <Sparkles size={15} className="text-emerald-400" />
                      <span>Ask AI Advisor to Resolve Passport Warnings</span>
                      <ArrowRight size={14} />
                    </button>
                  </div>
                </div>
              ) : (
                <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-3">
                  <RefreshCw size={32} className="mx-auto text-emerald-600 animate-spin" />
                  <p className="text-sm font-bold text-slate-700">Computing Compliance Passport...</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
