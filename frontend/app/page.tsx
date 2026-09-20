"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { isLoggedIn } from "@/lib/auth";

export default function RootPage() {
  const router = useRouter();

  useEffect(() => {
    if (isLoggedIn()) {
      router.push("/dashboard");
    } else {
      router.push("/login");
    }
  }, [router]);

  return (
    <div className="h-dvh bg-slate-900 flex items-center justify-center text-white text-xs">
      <div className="flex items-center gap-2">
        <div className="w-4 h-4 rounded-full bg-emerald-500 animate-spin" />
        <span>Loading IP-SAKTI Sahayak...</span>
      </div>
    </div>
  );
}
