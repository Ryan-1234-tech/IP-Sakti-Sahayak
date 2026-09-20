"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Leaf, ArrowRight, ShieldCheck, Sparkles } from "lucide-react";
import { saveUser, UserRole } from "@/lib/auth";
import LanguageSelector from "@/components/shared/LanguageSelector";

const ROLES: UserRole[] = [
  "AYUSH Startup",
  "MSME",
  "Researcher",
  "Innovator",
  "Student / Other",
];

export default function LoginPage() {
  const router = useRouter();
  const [isSignup, setIsSignup] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [org, setOrg] = useState("");
  const [role, setRole] = useState<UserRole>("AYUSH Startup");
  const [language, setLanguage] = useState("en");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const displayName = name.trim() || email.split("@")[0] || "Innovator";
    saveUser({
      name: displayName,
      org: org.trim() || "Herbal Health Co.",
      role,
      language,
    });
    router.push("/dashboard");
  };

  return (
    <div className="min-h-dvh bg-slate-900 flex items-center justify-center p-4 relative overflow-hidden font-sans">
      {/* Background Decorative Gradients */}
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-emerald-600/20 rounded-full blur-3xl" />
      <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-emerald-900/30 rounded-full blur-3xl" />

      <div className="max-w-md w-full bg-white/95 backdrop-blur-md rounded-2xl p-8 shadow-2xl border border-white/20 relative z-10">
        {/* Brand Identity */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-11 h-11 rounded-xl bg-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-900/30">
            <Leaf size={24} className="text-white" />
          </div>
          <div>
            <h1 className="font-bold text-xl text-slate-900 leading-tight">IP-SAKTI Sahayak</h1>
            <p className="text-xs text-emerald-700 font-semibold">Explainable IP & AYUSH Compliance Twin</p>
          </div>
        </div>

        <h2 className="text-lg font-bold text-slate-800 mb-1">
          {isSignup ? "Create Your Account" : "Sign In to Your Workspace"}
        </h2>
        <p className="text-xs text-slate-500 mb-6">
          Get cited legal guidance for Indian Patents, Trademarks, and AYUSH Regulations.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {isSignup && (
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Full Name</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Avantika Gupta"
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-600"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@startup.com"
              className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-600"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-600"
            />
          </div>

          {isSignup && (
            <>
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Organization / Startup Name</label>
                <input
                  type="text"
                  value={org}
                  onChange={(e) => setOrg(e.target.value)}
                  placeholder="e.g. AyushCare Bio Labs"
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-600"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">User Category / Role</label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value as UserRole)}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-600"
                >
                  {ROLES.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </select>
              </div>
            </>
          )}

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Preferred Language</label>
            <LanguageSelector value={language} onChange={setLanguage} className="w-full py-2.5" />
          </div>

          <button
            type="submit"
            className="w-full py-3 bg-emerald-700 hover:bg-emerald-600 text-white font-bold text-sm rounded-xl flex items-center justify-center gap-2 shadow-md transition-colors mt-6"
          >
            <span>{isSignup ? "Complete Registration" : "Sign In to Dashboard"}</span>
            <ArrowRight size={16} />
          </button>
        </form>

        <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-xs">
          <button
            onClick={() => setIsSignup(!isSignup)}
            className="text-emerald-700 font-semibold hover:underline"
          >
            {isSignup ? "Already have an account? Sign In" : "Don't have an account? Sign Up"}
          </button>
        </div>

        <div className="mt-4 p-3 bg-emerald-50 rounded-xl border border-emerald-100 flex items-center gap-2 text-[11px] text-emerald-800">
          <ShieldCheck size={16} className="text-emerald-600 flex-shrink-0" />
          <span>Local demo session — no server password stored.</span>
        </div>
      </div>
    </div>
  );
}
