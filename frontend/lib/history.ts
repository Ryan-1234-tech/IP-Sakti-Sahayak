/**
 * lib/history.ts
 * localStorage-based conversation history helpers.
 * Persists across page refreshes; cleared on sign-out.
 */

const KEY = "ipsakti_history";
const MAX_SESSIONS = 20;

export interface HistorySession {
  id: string;           // conversation_id from the backend
  title: string;        // first user message, truncated
  createdAt: string;    // ISO timestamp
  messages: StoredMessage[];
}

export interface StoredMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Array<{ id: string; title: string; authority?: string; url?: string; document_type?: string; relevance_score?: number }>;
  confidence?: string;
  actions?: Array<{ step: number; description: string; required_documents: string[] }>;
  timestamp: string;
}

function loadAll(): HistorySession[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as HistorySession[]) : [];
  } catch {
    return [];
  }
}

function saveAll(sessions: HistorySession[]): void {
  localStorage.setItem(KEY, JSON.stringify(sessions.slice(0, MAX_SESSIONS)));
}

export function getAllSessions(): HistorySession[] {
  return loadAll();
}

export function getSession(id: string): HistorySession | null {
  return loadAll().find((s) => s.id === id) ?? null;
}

export function upsertSession(session: HistorySession): void {
  const all = loadAll().filter((s) => s.id !== session.id);
  saveAll([session, ...all]);
}

export function deleteSession(id: string): void {
  saveAll(loadAll().filter((s) => s.id !== id));
}

export function clearAllSessions(): void {
  localStorage.removeItem(KEY);
}

/** Derive a display title from the first user message */
export function makeTitle(firstMessage: string): string {
  return firstMessage.length > 50
    ? firstMessage.slice(0, 47) + "…"
    : firstMessage;
}
