"use client";

import { useState } from "react";
import { X, Sparkles, ArrowRight, CheckCircle, Shield, HelpCircle } from "lucide-react";
import { useRouter } from "next/navigation";

interface Props {
  onClose: () => void;
}

const STEP_1_OPTIONS = [
  { id: "invention", title: "A new invention or formulation", desc: "Chemical composition, process, or herbal mix", icon: "🔬" },
  { id: "brand", title: "My product / brand name or logo", desc: "Wordmark, brand name, symbol, or slogan", icon: "™️" },
  { id: "content", title: "Written content, software, or artwork", desc: "Manuals, design, code, label artwork", icon: "©️" },
  { id: "tk", title: "Traditional knowledge or Ayurvedic remedy", desc: "Herbal formulation rooted in classical texts", icon: "🌿" },
];

const STEP_2_OPTIONS = [
  { id: "disclosed", label: "Have you publicly disclosed this product/formula yet?", options: ["No, it's confidential", "Yes, on website / social media", "Sold in limited trial"] },
  { id: "commercial", label: "What is your commercialization status?", options: ["Idea / Prototype stage", "Ready for launch", "Already manufacturing & selling"] },
];

export default function WizardModal({ onClose }: Props) {
  const router = useRouter();
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [selectedType, setSelectedType] = useState<string>("invention");
  const [disclosed, setDisclosed] = useState<string>("No, it's confidential");
  const [commercial, setCommercial] = useState<string>("Idea / Prototype stage");

  const handleFinish = () => {
    let prompt = "";
    if (selectedType === "invention") {
      prompt = `I have a new technical invention / formulation. Disclosure status: ${disclosed}. Stage: ${commercial}. What patent or IP protection do I need under Indian law, and what are my immediate next steps?`;
    } else if (selectedType === "brand") {
      prompt = `I want to protect my brand name and logo under Indian Trademark law. Stage: ${commercial}. Which class should I register under and what is the registration process?`;
    } else if (selectedType === "content") {
      prompt = `I want to copyright my artwork / written documentation. Disclosure status: ${disclosed}. How do I register copyright in India?`;
    } else {
      prompt = `I am developing an Ayurvedic herbal formulation based on traditional knowledge. Disclosure status: ${disclosed}. Stage: ${commercial}. How do I avoid Section 3(p) Patent rejection and TKDL prior-art issues?`;
    }

    onClose();
    router.push(`/chat?prompt=${encodeURIComponent(prompt)}`);
  };

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fade-up">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 rounded-lg p-1 hover:bg-slate-100 transition-colors"
        >
          <X size={18} />
        </button>

        {/* Wizard Header */}
        <div className="flex items-center gap-2 mb-1">
          <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-xs">
            {step}/3
          </div>
          <div>
            <h3 className="font-bold text-base text-slate-900">"What IP Do I Need?" Wizard</h3>
            <p className="text-xs text-slate-500">Answer 2 simple questions to get personalized IP recommendations</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden my-4">
          <div
            className="h-full bg-emerald-600 rounded-full transition-all duration-300"
            style={{ width: `${(step / 3) * 100}%` }}
          />
        </div>

        {/* Step 1: Protection Target */}
        {step === 1 && (
          <div className="space-y-3 py-2">
            <p className="text-sm font-semibold text-slate-800">Step 1: What are you trying to protect?</p>
            <div className="space-y-2">
              {STEP_1_OPTIONS.map((opt) => (
                <button
                  key={opt.id}
                  onClick={() => setSelectedType(opt.id)}
                  className={`w-full text-left p-3.5 rounded-xl border flex items-start gap-3 transition-all ${
                    selectedType === opt.id
                      ? "border-emerald-500 bg-emerald-50/60 ring-2 ring-emerald-200"
                      : "border-slate-200 hover:border-emerald-300 hover:bg-slate-50"
                  }`}
                >
                  <span className="text-xl">{opt.icon}</span>
                  <div>
                    <p className="text-xs font-bold text-slate-900">{opt.title}</p>
                    <p className="text-[11px] text-slate-500 mt-0.5">{opt.desc}</p>
                  </div>
                </button>
              ))}
            </div>
            <button
              onClick={() => setStep(2)}
              className="w-full mt-4 py-3 bg-emerald-700 hover:bg-emerald-600 text-white font-semibold text-sm rounded-xl flex items-center justify-center gap-2 transition-colors shadow-xs"
            >
              <span>Next: Business Stage</span>
              <ArrowRight size={16} />
            </button>
          </div>
        )}

        {/* Step 2: Context Details */}
        {step === 2 && (
          <div className="space-y-4 py-2">
            <p className="text-sm font-semibold text-slate-800">Step 2: Business &amp; Disclosure Details</p>
            
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-700">Public Disclosure Status:</label>
              <div className="space-y-1.5">
                {STEP_2_OPTIONS[0].options.map((opt) => (
                  <button
                    key={opt}
                    onClick={() => setDisclosed(opt)}
                    className={`w-full text-left px-3.5 py-2.5 rounded-lg border text-xs font-medium transition-all ${
                      disclosed === opt
                        ? "border-emerald-500 bg-emerald-50 text-emerald-800 font-bold"
                        : "border-slate-200 text-slate-600 hover:bg-slate-50"
                    }`}
                  >
                    {opt}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-700">Commercialization Stage:</label>
              <div className="space-y-1.5">
                {STEP_2_OPTIONS[1].options.map((opt) => (
                  <button
                    key={opt}
                    onClick={() => setCommercial(opt)}
                    className={`w-full text-left px-3.5 py-2.5 rounded-lg border text-xs font-medium transition-all ${
                      commercial === opt
                        ? "border-emerald-500 bg-emerald-50 text-emerald-800 font-bold"
                        : "border-slate-200 text-slate-600 hover:bg-slate-50"
                    }`}
                  >
                    {opt}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex gap-2 pt-2">
              <button
                onClick={() => setStep(1)}
                className="flex-1 py-2.5 border border-slate-200 text-slate-600 hover:bg-slate-50 font-medium text-xs rounded-xl"
              >
                Back
              </button>
              <button
                onClick={() => setStep(3)}
                className="flex-2 py-2.5 bg-emerald-700 hover:bg-emerald-600 text-white font-semibold text-xs rounded-xl flex items-center justify-center gap-2"
              >
                <span>Generate Assessment</span>
                <Sparkles size={14} />
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Recommendation Preview */}
        {step === 3 && (
          <div className="space-y-4 py-2">
            <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl space-y-2">
              <div className="flex items-center gap-2 text-emerald-800 font-bold text-sm">
                <CheckCircle size={18} className="text-emerald-600" />
                <span>Recommended IP Protection Roadmap</span>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed">
                Based on your input, IP-SAKTI Sahayak will generate a full statutory assessment grounded in Indian law.
              </p>
              <div className="bg-white p-3 rounded-lg border border-emerald-100 text-xs space-y-1 text-slate-800 font-medium">
                <p>📌 Target: <span className="font-bold capitalize">{selectedType}</span></p>
                <p>📌 Disclosure: <span>{disclosed}</span></p>
                <p>📌 Stage: <span>{commercial}</span></p>
              </div>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setStep(2)}
                className="flex-1 py-3 border border-slate-200 text-slate-600 hover:bg-slate-50 font-medium text-xs rounded-xl"
              >
                Back
              </button>
              <button
                onClick={handleFinish}
                className="flex-2 py-3 bg-emerald-700 hover:bg-emerald-600 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2 shadow-xs"
              >
                <span>Ask AI Advisor Now</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
