"use client";

import { SourceRef } from "@/lib/api";
import { ExternalLink, BookOpen } from "lucide-react";

interface Props {
  source: SourceRef;
  index: number;
}

export default function SourceCard({ source, index }: Props) {
  const isIndia = (source.jurisdiction || "INDIA").toUpperCase() === "INDIA";
  const provision = source.section || source.article || source.rule;
  const pageNum = source.page_number || source.page;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-3.5 shadow-2xs hover:shadow-xs transition-all flex flex-col justify-between group">
      <div>
        {/* Header: [Index] + Authority + Jurisdiction Badge */}
        <div className="flex items-center justify-between gap-2 mb-1.5">
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] font-bold text-emerald-800 bg-emerald-100 px-1.5 py-0.5 rounded">
              [{index}]
            </span>
            <span className="text-xs font-bold text-slate-800 truncate">
              {source.authority || "Official Authority"}
            </span>
          </div>

          <span
            className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${
              isIndia
                ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                : "bg-indigo-50 text-indigo-700 border-indigo-200"
            }`}
          >
            {isIndia ? "🇮🇳 INDIA" : "🌐 INTERNATIONAL"}
          </span>
        </div>

        {/* Source Title */}
        <h4 className="text-xs font-bold text-slate-900 leading-snug group-hover:text-emerald-700 transition-colors">
          {source.title}
        </h4>

        {/* Section / Article / Rule & Page number */}
        <div className="flex flex-wrap items-center gap-2 mt-2 text-[11px] text-slate-600 font-medium">
          {provision && (
            <span className="bg-slate-100 px-2 py-0.5 rounded text-slate-800 font-semibold">
              {provision}
            </span>
          )}
          {pageNum && (
            <span className="text-slate-500">
              Page {pageNum}
            </span>
          )}
          {source.relevance_score !== undefined && source.relevance_score !== null && (
            <span className="ml-auto text-[10px] text-emerald-700 font-bold">
              {Math.round(source.relevance_score * 100)}% match
            </span>
          )}
        </div>

        {/* Snippet Preview */}
        {source.snippet && (
          <p className="text-[11px] text-slate-500 mt-2 line-clamp-2 leading-relaxed bg-slate-50 p-1.5 rounded border border-slate-100">
            &ldquo;{source.snippet}&rdquo;
          </p>
        )}
      </div>

      {/* Footer / View Source link */}
      <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between">
        <span className="text-[10px] text-slate-400 capitalize">
          {source.source_type || source.document_type || "Guideline"}
        </span>

        {source.url || source.source_url ? (
          <a
            href={source.url || source.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 hover:text-emerald-800 hover:underline"
          >
            <span>View Source</span>
            <ExternalLink size={12} />
          </a>
        ) : (
          <span className="text-[10px] text-slate-400">Indexed Official Corpus</span>
        )}
      </div>
    </div>
  );
}
