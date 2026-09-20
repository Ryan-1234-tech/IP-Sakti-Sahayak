"use client";

import { useState } from "react";
import AppShell from "@/components/layout/AppShell";
import { UploadCloud, Clock, AlertTriangle, FileText, CheckCircle, ArrowRight, BookOpen } from "lucide-react";

export default function DocumentAnalyzerPage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [docId, setDocId] = useState<string | null>(null);
  const [extractedPreview, setExtractedPreview] = useState("");
  const [result, setResult] = useState<any>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || !e.target.files[0]) return;
    const selected = e.target.files[0];
    setFile(selected);
    setUploading(true);

    const formData = new FormData();
    formData.append("file", selected);

    try {
      const res = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setDocId(data.document_id);
      setExtractedPreview(data.extracted_text_preview);

      // Trigger analysis
      handleAnalyze(data.document_id);
    } catch (err) {
      console.error("Upload error", err);
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyze = async (id: string) => {
    setAnalyzing(true);
    try {
      const res = await fetch("http://localhost:8000/api/document/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ document_id: id }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error("Analyze error", err);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <AppShell>
      <div className="h-full overflow-y-auto p-8 max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-gradient-to-r from-[#0c1911] via-slate-900 to-emerald-950 rounded-2xl p-6 text-white shadow-xl flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-600/30 text-amber-300 border border-amber-500/40">
                PyMuPDF + Tesseract OCR Engine
              </span>
            </div>
            <h1 className="font-bold text-xl text-white">Government Document &amp; Deadline Extractor</h1>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl">
              Upload Patent Examination Reports, Office Actions, Trademark Notices, or Certificates to automatically extract deadlines, objections, and filing requirements.
            </p>
          </div>
          <Clock size={32} className="text-amber-400 opacity-80 flex-shrink-0" />
        </div>

        {/* File Upload Zone */}
        <div className="bg-white rounded-2xl border-2 border-dashed border-slate-300 hover:border-emerald-500 p-8 text-center transition-all cursor-pointer bg-slate-50/50">
          <input type="file" accept=".pdf" onChange={handleUpload} className="hidden" id="pdf-upload" />
          <label htmlFor="pdf-upload" className="cursor-pointer flex flex-col items-center">
            <div className="w-14 h-14 rounded-2xl bg-amber-100 text-amber-800 flex items-center justify-center mb-3">
              <UploadCloud size={28} />
            </div>
            <h3 className="font-bold text-sm text-slate-900">
              {file ? file.name : "Click to Upload Official Government PDF / Notice"}
            </h3>
            <p className="text-xs text-slate-500 mt-1">Supports Patent Office Actions, Trademark Reports, Form Notices (PDF up to 25MB)</p>
            {uploading && <p className="text-xs font-bold text-emerald-700 mt-2">Extracting text &amp; running OCR...</p>}
          </label>
        </div>

        {/* Results */}
        {result && (
          <div className="space-y-6">
            {/* Deadline Banner */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
              <h2 className="font-bold text-xs uppercase tracking-wider text-slate-400 mb-3">IMPORTANT DEADLINES DETECTED</h2>
              {result.deadline?.deadline_date ? (
                <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Clock size={24} className="text-amber-600" />
                    <div>
                      <h3 className="font-bold text-sm text-amber-900">Response Deadline: {result.deadline.deadline_date}</h3>
                      <p className="text-xs text-amber-800">{result.deadline.description}</p>
                    </div>
                  </div>
                  <span className="px-3 py-1 bg-amber-600 text-white rounded-lg font-bold text-xs uppercase tracking-wider">
                    Priority HIGH
                  </span>
                </div>
              ) : (
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600 font-medium">
                  ℹ️ {result.deadline?.description || "Could not identify a deadline in the uploaded document."}
                </div>
              )}
            </div>

            {/* Classification & Summary */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div>
                  <span className="text-[10px] font-bold text-slate-400 uppercase">Document Classification</span>
                  <h3 className="font-bold text-base text-slate-900 capitalize">{result.summary?.doc_type?.replace("_", " ")}</h3>
                </div>
                <span className="px-3 py-1 bg-emerald-100 text-emerald-800 font-bold text-xs rounded-full border border-emerald-300">
                  {result.confidence} Confidence ({round(result.confidence_score * 100)}%)
                </span>
              </div>

              <div>
                <h4 className="text-xs font-bold text-slate-700 uppercase mb-1">AI Executive Summary</h4>
                <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-3.5 rounded-xl border border-slate-200">
                  {result.summary?.summary}
                </p>
              </div>

              {result.requirements && result.requirements.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-slate-700 uppercase mb-2">Required Actions &amp; Compliance Steps</h4>
                  <div className="space-y-1.5">
                    {result.requirements.map((req: string, idx: number) => (
                      <div key={idx} className="flex items-center gap-2 text-xs text-slate-800 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                        <CheckCircle size={14} className="text-emerald-600 flex-shrink-0" />
                        <span>{req}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}

function round(val: number) {
  return Math.round(val || 0);
}
