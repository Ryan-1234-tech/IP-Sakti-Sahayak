/**
 * lib/auth.ts
 * localStorage-based auth helpers for demo purposes.
 * No server calls — stores user profile in browser storage.
 */

export type UserRole = "AYUSH Startup" | "MSME" | "Researcher" | "Innovator" | "Student / Other";

export interface UserProfile {
  name: string;
  org: string;
  role: UserRole;
  language: string; // BCP-47: "en", "hi", "ta", etc.
}

const KEY = "ipsakti_user";

export function getUser(): UserProfile | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as UserProfile) : null;
  } catch {
    return null;
  }
}

export function saveUser(profile: UserProfile): void {
  localStorage.setItem(KEY, JSON.stringify(profile));
}

export function clearUser(): void {
  localStorage.removeItem(KEY);
}

export function isLoggedIn(): boolean {
  return getUser() !== null;
}

/** Returns a time-of-day greeting */
export function greeting(name: string): string {
  const h = new Date().getHours();
  const tod = h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening";
  return `${tod}, ${name.split(" ")[0]}!`;
}
