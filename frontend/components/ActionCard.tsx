"use client";

import { Action } from "@/lib/api";

interface Props {
  actions: Action[];
  deadline?: { deadline_date?: string; description?: string };
}

export default function ActionCard({ actions, deadline }: Props) {
  if (!actions.length && !deadline) return null;

  return (
    <div className="rounded-2xl border border-indigo-500/30 bg-gradient-to-br from-indigo-500/10 to-violet-600/5 p-4 space-y-4">
      {/* Deadline banner */}
      {deadline?.deadline_date && (
        <div className="flex items-center gap-3 bg-rose-500/15 border border-rose-500/30 rounded-xl px-4 py-2.5">
          <span className="text-rose-400 text-lg" aria-hidden="true">⏰</span>
          <div>
            <p className="text-xs font-semibold text-rose-300 uppercase tracking-wider">
              Deadline
            </p>
            <p className="text-sm font-bold text-rose-200">{deadline.deadline_date}</p>
            {deadline.description && (
              <p className="text-xs text-rose-300/70 mt-0.5">{deadline.description}</p>
            )}
          </div>
        </div>
      )}

      {/* Next steps */}
      {actions.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest flex items-center gap-2">
            <span className="text-indigo-400" aria-hidden="true">→</span>
            Next Steps
          </h3>
          <ol className="space-y-2.5">
            {actions.map((action) => (
              <li key={action.step} className="flex gap-3">
                {/* Step number bubble */}
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-500/30 border border-indigo-500/50 flex items-center justify-center text-xs font-bold text-indigo-300">
                  {action.step}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-slate-200 leading-snug">
                    {action.description}
                  </p>
                  {action.required_documents.length > 0 && (
                    <ul className="mt-1.5 space-y-1">
                      {action.required_documents.map((doc, i) => (
                        <li
                          key={i}
                          className="flex items-center gap-1.5 text-xs text-slate-400"
                        >
                          <span
                            className="w-1 h-1 rounded-full bg-slate-500 flex-shrink-0"
                            aria-hidden="true"
                          />
                          {doc}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
