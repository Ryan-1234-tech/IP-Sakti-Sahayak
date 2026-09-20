import type { Metadata } from "next";
import "./globals.css";
import { JurisdictionProvider } from "@/lib/jurisdiction";

export const metadata: Metadata = {
  title: "IP-SAKTI Sahayak — Source-Cited IP & AYUSH Legal Guidance",
  description:
    "Explainable compliance digital twin for Indian IP law and AYUSH regulatory guidance. Every assessment is source-cited, confidence-scored, and paired with an actionable mitigation plan.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>
        <JurisdictionProvider>{children}</JurisdictionProvider>
      </body>
    </html>
  );
}
