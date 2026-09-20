"use client";

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import AppShell from "@/components/layout/AppShell";
import ChatPanel from "@/components/chat/ChatPanel";

function ChatContent() {
  const searchParams = useSearchParams();
  const prompt = searchParams.get("prompt");
  const session = searchParams.get("session");

  return <ChatPanel initialPrompt={prompt} sessionId={session} />;
}

export default function ChatPage() {
  return (
    <AppShell>
      <Suspense fallback={<div className="p-8 text-center text-xs text-slate-500">Loading advisor interface...</div>}>
        <ChatContent />
      </Suspense>
    </AppShell>
  );
}
