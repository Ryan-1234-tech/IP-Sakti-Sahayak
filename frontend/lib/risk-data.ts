/**
 * lib/risk-data.ts
 * Core data model and sample dataset for the IP-SAKTI Risk Radar.
 */

export type Priority = "HIGH" | "MEDIUM" | "LOW";
export type Category =
  | "IP & Patents"
  | "Advertisement & Claims"
  | "Licensing & Renewals"
  | "Traditional Knowledge"
  | "Quality & Standards";

export interface Evidence {
  clause: string;       // e.g. "Section 3(d), Patents Act 1970"
  excerpt: string;      // Quoted text from the legal document
  source: string;       // Human-readable source name
  url: string;          // Link to official source
}

export interface Risk {
  id: string;           // e.g. "IP-2026-001"
  displayId: string;    // e.g. "R-001"
  title: string;
  description: string;
  category: Category;
  priority: Priority;
  score: number;        // 0–100
  confidence: number;   // 0–100 %
  deadline: string;     // ISO date string "YYYY-MM-DD"
  escalated: boolean;
  evidence: Evidence;
  mitigation: string[];
}

// ─── Computed helpers ─────────────────────────────────────────────────────────

export function daysUntil(dateStr: string): number {
  const target = new Date(dateStr);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  target.setHours(0, 0, 0, 0);
  return Math.round((target.getTime() - today.getTime()) / 86_400_000);
}

// ─── Sample dataset ───────────────────────────────────────────────────────────

export const RISKS: Risk[] = [
  {
    id: "IP-2026-001",
    displayId: "R-001",
    title: "Unsubstantiated Efficacy Claim on Label",
    description:
      'Pack copy states "cures chronic diabetes in 30 days" without approved clinical substantiation, triggering prohibited-claims exposure.',
    category: "Advertisement & Claims",
    priority: "HIGH",
    score: 88,
    confidence: 96,
    deadline: "2026-09-15",
    escalated: true,
    evidence: {
      clause:
        "Section 3(d), Drugs & Magic Remedies (Objectionable Advertisements) Act, 1954",
      excerpt:
        '"No person shall take any part in the publication of any advertisement referring to any drug in terms which suggest or are calculated to lead to the use of that drug for the diagnosis, cure, mitigation, treatment or prevention of any disease specified in the Schedule."',
      source: "India Code — Ministry of Health & Family Welfare",
      url: "https://www.indiacode.nic.in/handle/123456789/1960",
    },
    mitigation: [
      "Remove the disease-specific curative wording from all primary and secondary packaging artwork.",
      "Replace with AYUSH-permissible structure/function language reviewed by the label committee.",
      "Attach clinical dossier or drop the claim; log the decision in the Document Vault.",
      "Re-submit artwork to the State Licensing Authority for endorsement before the next print run.",
    ],
  },
  {
    id: "IP-2026-002",
    displayId: "R-002",
    title: "TKDL Overlap in Botanical Formulation",
    description:
      "Ashwagandha–Guduchi combination shows prior-art overlap with a TKDL classical formulation, weakening novelty in the pending patent claim set.",
    category: "IP & Patents",
    priority: "MEDIUM",
    score: 62,
    confidence: 84,
    deadline: "2026-10-30",
    escalated: false,
    evidence: {
      clause:
        "Section 3(p), Patents Act 1970 — Traditional Knowledge exclusion",
      excerpt:
        '"An invention which, in effect, is traditional knowledge or which is an aggregation or duplication of known properties of traditionally known component or components is not an invention under this Act."',
      source: "Indian Patents Act 1970 — IP India",
      url: "https://ipindia.gov.in/acts.htm",
    },
    mitigation: [
      "Commission a formal freedom-to-operate (FTO) search against TKDL records before next USPTO/IPO filing.",
      "Amend claims to emphasise novel extraction process, bioavailability enhancement, or synergistic ratio rather than ingredient combination alone.",
      "Consult a registered patent agent to draft divisional claims around the novel delivery mechanism.",
      "File a TKDL disclosure statement in the patent application to demonstrate good-faith prior-art acknowledgment.",
    ],
  },
  {
    id: "IP-2026-003",
    displayId: "R-003",
    title: "Form 25-D Manufacturing Licence Renewal",
    description:
      "Ayurvedic manufacturing licence for the Unit-2 line lapses shortly; renewal file is incomplete without the updated GMP schedule-T certificate.",
    category: "Licensing & Renewals",
    priority: "HIGH",
    score: 91,
    confidence: 99,
    deadline: "2026-10-05",
    escalated: false,
    evidence: {
      clause:
        "Rule 157 & 158, Drugs & Cosmetics Rules 1945 — Renewal of Ayurvedic Licence",
      excerpt:
        '"A licence granted under this Chapter shall be valid for a period of five years from the date of issue, and shall be renewable for a further period of five years on payment of the prescribed fees provided an application for renewal is made before the date of expiry of the licence."',
      source: "Ministry of Health & Family Welfare — Drugs & Cosmetics Rules",
      url: "https://cdsco.gov.in/opencms/opencms/en/Drugs/Acts-Rules/",
    },
    mitigation: [
      "Obtain updated GMP Schedule-T inspection certificate from the State Drug Controller within 10 working days.",
      "Complete Form 25-D renewal package: inspection certificate, fees challan, and updated site master file.",
      "Submit the renewal application at least 30 days prior to licence expiry to prevent manufacturing stoppage.",
      "Engage a regulatory consultant to track application status with the State Licensing Authority.",
    ],
  },
  {
    id: "IP-2026-004",
    displayId: "R-004",
    title: "Trademark Opposition Window Closing",
    description:
      "A phonetically similar mark was published in the Trade Marks Journal for class 5; the opposition window is narrowing.",
    category: "IP & Patents",
    priority: "LOW",
    score: 44,
    confidence: 78,
    deadline: "2026-11-20",
    escalated: false,
    evidence: {
      clause: "Section 21, Trade Marks Act 1999 — Opposition to Registration",
      excerpt:
        '"Any person may, within four months from the date of advertisement or re-advertisement of an application for registration, give notice in writing in the prescribed manner and on payment of the prescribed fee, to the Registrar, of opposition to the registration."',
      source: "IP India — Trade Marks Registry",
      url: "https://ipindia.gov.in/trade-marks.htm",
    },
    mitigation: [
      "File a notice of opposition (Form TM-O) with the Trade Marks Registry before the 4-month window closes.",
      "Prepare a comparative phonetic analysis report showing likelihood of confusion with your registered mark.",
      "Gather evidence of prior use and market reputation: invoices, advertisements, social media reach.",
      "Engage a trade mark attorney to represent the opposition proceedings before the Registry.",
    ],
  },
  {
    id: "IP-2026-005",
    displayId: "R-005",
    title: "Heavy Metal Labelling Non-Compliance",
    description:
      "New AYUSH notification mandates declaration of heavy metal content per batch on the outer label; current label template does not include this field.",
    category: "Quality & Standards",
    priority: "MEDIUM",
    score: 71,
    confidence: 91,
    deadline: "2026-09-30",
    escalated: false,
    evidence: {
      clause:
        "AYUSH Notification SO 2732(E) — Heavy Metal Labelling Amendment, 2024",
      excerpt:
        '"Every manufacturer of Ayurvedic, Siddha, or Unani drugs containing heavy metals shall declare the concentration of each heavy metal per dosage unit on the label in the prescribed format with effect from the date of notification."',
      source: "Ministry of AYUSH — Official Gazette",
      url: "https://ayush.gov.in/notifications",
    },
    mitigation: [
      "Update the label template to include a dedicated heavy-metal declaration field per batch.",
      "Commission batch-wise heavy metal testing from a NABL-accredited laboratory.",
      "Coordinate with the packaging vendor to ensure revised labels are print-ready within 3 weeks.",
      "File revised label specimen with the State Drug Authority before the notification compliance date.",
    ],
  },
];

// ─── Aggregate stats ──────────────────────────────────────────────────────────

export function getStats(risks: Risk[]) {
  const today = new Date();
  const deadline45 = risks.filter((r) => {
    const d = daysUntil(r.deadline);
    return d >= 0 && d <= 45;
  });
  const avgScore = risks.length
    ? Math.round(risks.reduce((s, r) => s + r.score, 0) / risks.length)
    : 0;
  const complianceScore = Math.max(0, 100 - avgScore);
  return {
    complianceScore,
    activeRisks: risks.length,
    pendingDeadlines: deadline45.length,
    escalations: risks.filter((r) => r.escalated).length,
  };
}
