"use client";

import { useState, useCallback, useRef } from "react";
import { X, UploadCloud, FileText, CheckCircle, Loader2 } from "lucide-react";

interface Props {
  onClose: () => void;
  onComplete: () => void;
}

const STEPS = [
  "Parsing Document...",
  "Checking TKDL Database...",
  "Generating Risk Radar...",
];

export default function ScanModal({ onClose, onComplete }: Props) {
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [scanning, setScanning] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [progress, setProgress] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) setFile(dropped);
  }, []);

  const startScan = () => {
    if (!file) return;
    setScanning(true);
    setCurrentStep(0);
    setProgress(0);

    // Simulate 3 scan steps each ~1.5s
    let step = 0;
    const interval = setInterval(() => {
      step++;
      const prog = Math.round((step / STEPS.length) * 100);
      setProgress(prog);
      if (step < STEPS.length) {
        setCurrentStep(step);
      } else {
        clearInterval(interval);
        setCurrentStep(STEPS.length);
        setTimeout(() => {
          onComplete();
          onClose();
        }, 900);
      }
    }, 1600);
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-40"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-md bg-white rounded-2xl shadow-2xl p-6 animate-fade-up">
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="font-display text-lg font-bold text-slate-900">Scan New Product</h2>
            <p className="text-xs text-slate-400 mt-0.5">Upload a product dossier or label document</p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full hover:bg-slate-100 flex items-center justify-center text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X size={16} />
          </button>
        </div>

        {/* Drop zone */}
        {!scanning && (
          <>
            <div
              onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={onDrop}
              onClick={() => inputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all duration-200 mb-4 ${
                dragging
                  ? "border-emerald-400 bg-emerald-50"
                  : file
                  ? "border-emerald-400 bg-emerald-50"
                  : "border-slate-200 hover:border-emerald-300 hover:bg-slate-50 bg-slate-50/50"
              }`}
            >
              <input
                ref={inputRef}
                type="file"
                accept=".pdf,.docx,.doc"
                className="hidden"
                onChange={(e) => e.target.files?.[0] && setFile(e.target.files[0])}
              />
              {file ? (
                <>
                  <FileText size={30} className="text-emerald-600 mb-2" />
                  <p className="text-sm font-semibold text-emerald-700">{file.name}</p>
                  <p className="text-xs text-slate-400 mt-1">
                    {(file.size / 1024).toFixed(0)} KB — Click to change
                  </p>
                </>
              ) : (
                <>
                  <UploadCloud size={32} className="text-slate-300 mb-3" />
                  <p className="text-sm font-semibold text-slate-600">
                    Drag &amp; drop your file here
                  </p>
                  <p className="text-xs text-slate-400 mt-1">PDF or DOCX up to 20 MB</p>
                  <button className="mt-3 text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-lg hover:bg-emerald-100 transition-colors">
                    Browse files
                  </button>
                </>
              )}
            </div>

            <button
              onClick={startScan}
              disabled={!file}
              className={`w-full py-3 rounded-xl font-semibold text-sm transition-all duration-200 ${
                file
                  ? "bg-emerald-700 hover:bg-emerald-600 text-white shadow-md hover:shadow-lg"
                  : "bg-slate-100 text-slate-400 cursor-not-allowed"
              }`}
            >
              Start Analysis
            </button>
          </>
        )}

        {/* Scanning progress */}
        {scanning && (
          <div className="py-2">
            {/* Progress bar */}
            <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden mb-6">
              <div
                className="h-full bg-emerald-500 rounded-full transition-all duration-700"
                style={{ width: `${progress}%` }}
              />
            </div>

            {/* Steps */}
            <div className="flex flex-col gap-3">
              {STEPS.map((step, i) => {
                const done = i < currentStep;
                const active = i === currentStep;
                return (
                  <div key={step} className="flex items-center gap-3">
                    {done ? (
                      <CheckCircle size={18} className="text-emerald-500 flex-shrink-0" />
                    ) : active ? (
                      <Loader2 size={18} className="text-emerald-600 flex-shrink-0 animate-spin" />
                    ) : (
                      <div className="w-[18px] h-[18px] rounded-full border-2 border-slate-200 flex-shrink-0" />
                    )}
                    <span
                      className={`text-sm ${
                        done
                          ? "text-slate-400 line-through"
                          : active
                          ? "text-slate-900 font-semibold"
                          : "text-slate-400"
                      }`}
                    >
                      {step}
                    </span>
                  </div>
                );
              })}
            </div>

            {currentStep >= STEPS.length && (
              <div className="mt-5 text-center">
                <CheckCircle size={24} className="text-emerald-500 mx-auto mb-2" />
                <p className="text-sm font-semibold text-emerald-700">Scan complete! Loading results…</p>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}
