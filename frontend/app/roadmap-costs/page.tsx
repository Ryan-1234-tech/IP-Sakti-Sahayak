"use client";

import { useState, useEffect } from "react";
import AppShell from "@/components/layout/AppShell";
import { LayoutDashboard, CheckCircle, Calculator, Map, FileText, ArrowRight, Shield } from "lucide-react";

export default function RoadmapCostsPage() {
  const [activeIp, setActiveIp] = useState("patent");
  const [applicantType, setApplicantType] = useState("Startup");
  const [roadmap, setRoadmap] = useState<any[]>([]);
  const [checklist, setChecklist] = useState<any[]>([]);
  const [costData, setCostData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData(activeIp, applicantType);
  }, [activeIp, applicantType]);

  const fetchData = async (ip: string, appType: string) => {
    setLoading(true);
    try {
      // Fetch Roadmap
      const resRoadmap = await fetch(`http://localhost:8000/api/features/roadmap/${ip}`);
      const dataRoadmap = await resRoadmap.json();
      setRoadmap(dataRoadmap.steps || []);

      // Fetch Checklist
      const resChecklist = await fetch(`http://localhost:8000/api/features/compliance-checklist/${ip}`);
      const dataChecklist = await resChecklist.json();
      setChecklist(dataChecklist.checklist || []);

      // Fetch Cost Estimate
      const resCost = await fetch("http://localhost:8000/api/features/cost-estimator", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ip_type: ip, applicant_type: appType, application_type: "Standard" }),
      });
      const dataCost = await resCost.json();
      setCostData(dataCost);
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
        <div className="bg-gradient-to-r from-[#0c1911] via-emerald-950 to-slate-900 rounded-2xl p-6 text-white shadow-xl flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-600/30 text-emerald-300 border border-emerald-500/40">
                Official Indian Patent &amp; TM Gazettes
              </span>
            </div>
            <h1 className="font-bold text-xl text-white">IP Step-by-Step Roadmap &amp; Official Fee Cost Estimator</h1>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl">
              Dynamic roadmap timelines, required application documents, and official government fee schedules tailored by IP category and entity type.
            </p>
          </div>
        </div>

        {/* IP Category Selector Tabs */}
        <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
          {["patent", "trademark", "design", "copyright", "gi"].map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveIp(cat)}
              className={`px-4 py-2 rounded-xl text-xs font-bold capitalize transition-all ${
                activeIp === cat
                  ? "bg-emerald-800 text-white shadow-md"
                  : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
              }`}
            >
              {cat.toUpperCase()}
            </button>
          ))}
        </div>

        {/* Cost Estimator Box */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h2 className="font-bold text-xs uppercase tracking-wider text-slate-800 flex items-center gap-2">
              <Calculator size={16} className="text-emerald-700" />
              <span>Official Government Fee Estimator ({activeIp.toUpperCase()})</span>
            </h2>

            <div className="flex items-center gap-2 text-xs">
              <span className="font-bold text-slate-500">Applicant Entity:</span>
              <select
                value={applicantType}
                onChange={(e) => setApplicantType(e.target.value)}
                className="text-xs font-bold p-1.5 rounded-lg border border-slate-300 bg-slate-50 text-slate-900"
              >
                <option value="Individual">Natural Person / Individual</option>
                <option value="Startup">Startup (80% Concession)</option>
                <option value="MSME">Small Entity / MSME (80% Concession)</option>
                <option value="Educational">Educational Institution</option>
                <option value="Enterprise">Large Entity / Others</option>
              </select>
            </div>
          </div>

          {costData && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200">
                <span className="text-[10px] font-bold text-emerald-800 uppercase">Estimated Official Fee</span>
                <p className="text-2xl font-extrabold text-emerald-900 mt-1">₹{costData.estimated_official_fee?.toLocaleString("en-IN")}</p>
                <span className="text-[10px] text-emerald-700 block mt-1">Excludes professional agent fees</span>
              </div>

              <div className="md:col-span-2 space-y-2">
                <h4 className="text-xs font-bold text-slate-700 uppercase">Fee Breakdown</h4>
                {costData.fee_breakdown?.map((item: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between text-xs bg-slate-50 p-2.5 rounded-lg border border-slate-200">
                    <div>
                      <span className="font-bold text-slate-800">{item.head}</span>
                      <p className="text-[10px] text-slate-500">{item.note}</p>
                    </div>
                    <span className="font-extrabold text-slate-900">₹{item.fee_inr?.toLocaleString("en-IN")}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Dynamic Roadmap */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <h2 className="font-bold text-xs uppercase tracking-wider text-slate-800 flex items-center gap-2 border-b border-slate-100 pb-3">
            <Map size={16} className="text-emerald-700" />
            <span>Step-by-Step Procedure Roadmap ({activeIp.toUpperCase()})</span>
          </h2>

          <div className="space-y-3">
            {roadmap.map((step: any, idx: number) => (
              <div key={idx} className="flex items-start gap-4 p-4 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition-colors">
                <div className="w-8 h-8 rounded-xl bg-emerald-800 text-white font-bold text-xs flex items-center justify-center flex-shrink-0">
                  {step.step_number}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-sm text-slate-900">{step.title}</h3>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-300">
                      ⏱ {step.timeline}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 mt-1 leading-relaxed">{step.description}</p>
                  {step.required_documents && step.required_documents.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {step.required_documents.map((doc: string, dIdx: number) => (
                        <span key={dIdx} className="text-[10px] font-semibold px-2 py-0.5 bg-slate-200 text-slate-800 rounded">
                          📄 {doc}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Dynamic Application Checklist */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <h2 className="font-bold text-xs uppercase tracking-wider text-slate-800 flex items-center gap-2 border-b border-slate-100 pb-3">
            <FileText size={16} className="text-emerald-700" />
            <span>Application Document &amp; Legal Requirement Checklist</span>
          </h2>

          <div className="space-y-2">
            {checklist.map((item: any, idx: number) => (
              <div key={idx} className="p-3.5 rounded-xl border border-slate-200 bg-slate-50 flex items-start gap-3">
                <CheckCircle size={18} className="text-emerald-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-xs text-slate-900">{item.item}</h4>
                    <span className="text-[10px] font-semibold text-slate-500">{item.relevant_provision}</span>
                  </div>
                  <p className="text-xs text-slate-600 mt-0.5">{item.explanation}</p>
                  <p className="text-[10px] text-emerald-800 font-semibold mt-1">Why Needed: {item.why_needed}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
