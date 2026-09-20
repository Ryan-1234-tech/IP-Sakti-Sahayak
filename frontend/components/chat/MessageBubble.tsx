"use client";

import { useState } from "react";
import { CheckCircle2, ThumbsUp, ThumbsDown, Volume2, VolumeX, Shield, Sparkles } from "lucide-react";
import { SourceRef, Action, submitFeedback } from "@/lib/api";

interface MessageProps {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceRef[];
  confidence?: string;
  actions?: Action[];
  timestamp: string;
  onSelectEvidence?: (source: SourceRef) => void;
}

export default function MessageBubble({
  id,
  role,
  content,
  sources,
  confidence,
  actions,
  timestamp,
  onSelectEvidence,
}: MessageProps) {
  const [rating, setRating] = useState<number | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const handleRating = async (value: 1 | -1) => {
    if (rating === value) return;
    setRating(value);
    try {
      await submitFeedback({ message_id: id, rating: value });
    } catch {
      // Ignore background rating errors
    }
  };

  const handleSpeak = () => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    const cleanText = content.replace(/[*_#`[\]()]/g, "");
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
    setIsSpeaking(true);
  };

  return (
    <div className={`flex flex-col ${role === "user" ? "items-end" : "items-start"}`}>
      <div
        className={`max-w-[85%] rounded-2xl p-4.5 shadow-xs ${
          role === "user"
            ? "bg-emerald-700 text-white rounded-br-none"
            : "bg-white border border-slate-200 text-slate-900 rounded-bl-none"
        }`}
      >
        {/* Assistant Header */}
        {role === "assistant" && (
          <div className="flex items-center justify-between border-b border-slate-100 pb-2.5 mb-3">
            <div className="flex items-center gap-2">
              <span className="w-5 h-5 rounded-md bg-emerald-100 text-emerald-800 flex items-center justify-center text-[10px] font-bold">
                IP
              </span>
              <span className="text-xs font-bold text-slate-800">IP-SAKTI Sahayak Response</span>
            </div>
            
            <div className="flex items-center gap-2">
              {/* Text to speech button */}
              <button
                onClick={handleSpeak}
                className={`p-1 rounded hover:bg-slate-100 text-slate-500 transition-colors flex items-center gap-1 text-[11px] font-semibold ${
                  isSpeaking ? "text-emerald-600 bg-emerald-50" : ""
                }`}
                title="Listen to response"
              >
                {isSpeaking ? <VolumeX size={14} /> : <Volume2 size={14} />}
                <span className="hidden sm:inline">{isSpeaking ? "Stop" : "Listen"}</span>
              </button>

              {confidence && (
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                    confidence === "HIGH"
                      ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                      : confidence === "MEDIUM"
                      ? "bg-amber-50 text-amber-700 border-amber-200"
                      : "bg-rose-50 text-rose-700 border-rose-200"
                  }`}
                >
                  Confidence: {confidence}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Text Content */}
        <div className="text-sm leading-relaxed whitespace-pre-line">{content}</div>

        {/* Recommended Action Steps */}
        {actions && actions.length > 0 && (
          <div className="mt-4 pt-3 border-t border-slate-100">
            <p className="text-xs font-bold text-slate-700 flex items-center gap-1.5 mb-2">
              <CheckCircle2 size={14} className="text-emerald-600" />
              <span>Recommended Action Steps:</span>
            </p>
            <div className="space-y-1.5">
              {actions.map((act, i) => (
                <div key={i} className="flex items-start gap-2 text-xs text-slate-700 bg-slate-50 p-2 rounded-lg border border-slate-100">
                  <span className="font-bold text-emerald-700 flex-shrink-0">{i + 1}.</span>
                  <span>{act.description}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Cited Evidence Sources */}
        {sources && sources.length > 0 && (
          <div className="mt-3 pt-2 flex flex-wrap items-center gap-1.5">
            <span className="text-[10px] font-semibold text-slate-400">Cited Evidence:</span>
            {sources.map((src, i) => (
              <button
                key={i}
                onClick={() => onSelectEvidence?.(src)}
                title="Click to inspect verified legal excerpt & statutory clause"
                className="inline-flex items-center gap-1.5 text-[11px] font-medium bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 hover:border-emerald-400 px-2.5 py-1 rounded-lg shadow-2xs hover:shadow-xs active:scale-95 transition-all cursor-pointer group"
              >
                <span>📖</span>
                <span className="font-semibold underline decoration-emerald-300 group-hover:decoration-emerald-700 underline-offset-2">
                  {src.title || src.id}
                </span>
                {src.relevance_score !== undefined && src.relevance_score !== null && (
                  <span className="text-[9px] font-bold bg-emerald-200/70 text-emerald-900 px-1.5 py-0.2 rounded-full">
                    {Math.round(src.relevance_score * 100)}%
                  </span>
                )}
              </button>
            ))}
          </div>
        )}

        {/* Assistant Feedback Controls & Statutory Disclaimer */}
        {role === "assistant" && (
          <div className="mt-3 pt-2.5 border-t border-slate-100 space-y-1.5">
            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <span className="italic text-slate-500 font-medium">
                ⚖️ Information provided for guidance only, not legal advice.
              </span>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => handleRating(1)}
                  className={`p-1 rounded hover:bg-slate-100 transition-colors ${
                    rating === 1 ? "text-emerald-600 font-bold" : "text-slate-400"
                  }`}
                  title="Helpful response"
                >
                  <ThumbsUp size={13} />
                </button>
                <button
                  onClick={() => handleRating(-1)}
                  className={`p-1 rounded hover:bg-slate-100 transition-colors ${
                    rating === -1 ? "text-rose-600 font-bold" : "text-slate-400"
                  }`}
                  title="Unhelpful response"
                >
                  <ThumbsDown size={13} />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <span className="text-[10px] text-slate-400 mt-1 px-1">{timestamp}</span>
    </div>
  );
}
