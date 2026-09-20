import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // No API rewrites — the browser fetches directly to http://localhost:8000
  // (CORS is configured on the backend). Next.js rewrites cannot handle long
  // Ollama responses (30-120s) and drop them with ECONNRESET.
};

export default nextConfig;
