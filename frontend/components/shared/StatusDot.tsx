"use client";

import { useEffect, useState } from "react";
import { getHealth, HealthResponse } from "@/lib/api";

export default function StatusDot() {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    let mounted = true;
    const check = async () => {
      try {
        const res = await getHealth();
        if (mounted) setHealth(res);
      } catch {
        if (mounted) {
          setHealth({
            status: "offline",
            version: "0.1.0",
            llm_provider: "ollama",
            llm_model: "llama3.2",
            llm_configured: false,
            kb_chunk_count: 0,
            message: "Backend offline",
          } as HealthResponse);
        }
      }
    };
    check();
    const interval = setInterval(check, 15000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const isOk = health?.llm_configured ?? false;

  return (
    <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs text-slate-300">
      <span className="relative flex h-2 w-2">
        {isOk ? (
          <>
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </>
        ) : (
          <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
        )}
      </span>
      <span className="truncate max-w-[150px]">
        {isOk ? `Ollama (${health?.llm_model || "Active"})` : "Ollama Disconnected"}
      </span>
    </div>
  );
}
