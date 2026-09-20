"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Clock, Plus, Trash2 } from "lucide-react";
import { getAllSessions, deleteSession, HistorySession } from "@/lib/history";

export default function HistorySidebar() {
  const router = useRouter();
  const [sessions, setSessions] = useState<HistorySession[]>([]);

  useEffect(() => {
    setSessions(getAllSessions());
  }, []);

  const handleDelete = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    deleteSession(id);
    setSessions(getAllSessions());
  };

  if (sessions.length === 0) return null;

  return (
    <div className="mt-4 pt-4 border-t border-white/10">
      <div className="flex items-center justify-between px-2 mb-2">
        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1">
          <Clock size={12} />
          Recent Chats
        </span>
        <button
          onClick={() => router.push("/chat")}
          className="text-emerald-400 hover:text-emerald-300 text-[10px] font-semibold flex items-center gap-0.5"
        >
          <Plus size={12} />
          New
        </button>
      </div>

      <div className="space-y-1 max-h-48 overflow-y-auto pr-1">
        {sessions.map((sess) => (
          <div
            key={sess.id}
            onClick={() => router.push(`/chat?session=${sess.id}`)}
            className="group flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs text-slate-300 hover:text-white hover:bg-white/10 cursor-pointer transition-colors"
          >
            <span className="truncate flex-1">{sess.title}</span>
            <button
              onClick={(e) => handleDelete(e, sess.id)}
              className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-rose-400 p-0.5 transition-opacity"
              title="Delete session"
            >
              <Trash2 size={12} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
