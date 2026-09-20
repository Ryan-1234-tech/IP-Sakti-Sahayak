"use client";

import { useCallback, useRef, useState } from "react";
import { uploadDocument, UploadResponse } from "@/lib/api";

interface Props {
  onUploaded: (response: UploadResponse) => void;
}

type UploadState = "idle" | "dragging" | "uploading" | "done" | "error";

export default function UploadZone({ onUploaded }: Props) {
  const [state, setState] = useState<UploadState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<string>("");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(
    async (file: File) => {
      if (!file.name.toLowerCase().endsWith(".pdf")) {
        setError("Only PDF files are supported.");
        setState("error");
        return;
      }
      if (file.size > 20 * 1024 * 1024) {
        setError("File exceeds the 20 MB limit.");
        setState("error");
        return;
      }

      setState("uploading");
      setProgress("Uploading…");
      setError(null);

      try {
        setProgress("Extracting text…");
        const response = await uploadDocument(file);
        setState("done");
        onUploaded(response);
      } catch (err) {
        setError((err as Error).message ?? "Upload failed. Please try again.");
        setState("error");
      }
    },
    [onUploaded]
  );

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setState("idle");
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const onInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const isDragging = state === "dragging";
  const isUploading = state === "uploading";

  return (
    <div
      className={`relative rounded-2xl border-2 border-dashed p-8 text-center transition-all duration-300 cursor-pointer
        ${isDragging ? "border-indigo-400 bg-indigo-500/10 scale-[1.01]" : "border-slate-700 bg-slate-900/50 hover:border-slate-600 hover:bg-slate-900/80"}
        ${isUploading ? "pointer-events-none opacity-70" : ""}
      `}
      onDragOver={(e) => { e.preventDefault(); setState("dragging"); }}
      onDragLeave={() => setState("idle")}
      onDrop={onDrop}
      onClick={() => !isUploading && inputRef.current?.click()}
      role="button"
      aria-label="Upload PDF document"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,application/pdf"
        className="hidden"
        onChange={onInputChange}
        id="pdf-upload-input"
        aria-label="Choose a PDF file"
      />

      {isUploading ? (
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
          <p className="text-slate-300 text-sm">{progress}</p>
        </div>
      ) : state === "error" ? (
        <div className="flex flex-col items-center gap-2">
          <span className="text-3xl">⚠️</span>
          <p className="text-rose-400 text-sm">{error}</p>
          <button
            className="text-xs text-slate-400 underline mt-1"
            onClick={(e) => { e.stopPropagation(); setState("idle"); setError(null); }}
          >
            Try again
          </button>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center text-2xl">
            📄
          </div>
          <div>
            <p className="text-slate-200 font-medium text-sm">
              {isDragging ? "Drop your PDF here" : "Drag & drop a PDF"}
            </p>
            <p className="text-slate-500 text-xs mt-1">
              or click to browse · Max 20 MB
            </p>
          </div>
          <p className="text-xs text-slate-600">
            Examination notices, certificates, applications, guidelines
          </p>
        </div>
      )}
    </div>
  );
}
