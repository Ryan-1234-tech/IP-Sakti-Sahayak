"use client";

interface Props {
  confidence: "HIGH" | "MEDIUM" | "LOW" | string;
  score?: number;
  reasons?: string[];
}

const CONFIG = {
  HIGH: {
    label: "High Confidence",
    emoji: "✓",
    bg: "bg-emerald-500/15 border-emerald-500/40",
    text: "text-emerald-300",
    dot: "bg-emerald-400",
    glow: "shadow-emerald-500/20",
  },
  MEDIUM: {
    label: "Medium Confidence",
    emoji: "~",
    bg: "bg-amber-500/15 border-amber-500/40",
    text: "text-amber-300",
    dot: "bg-amber-400",
    glow: "shadow-amber-500/20",
  },
  LOW: {
    label: "Low Confidence",
    emoji: "!",
    bg: "bg-rose-500/15 border-rose-500/40",
    text: "text-rose-300",
    dot: "bg-rose-400",
    glow: "shadow-rose-500/20",
  },
} as const;

export default function ConfidenceBadge({ confidence, score, reasons }: Props) {
  const cfg = CONFIG[confidence as keyof typeof CONFIG] ?? CONFIG.LOW;

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold shadow-lg ${cfg.bg} ${cfg.text} ${cfg.glow}`}
      title={reasons?.join("\n")}
    >
      <span
        className={`w-2 h-2 rounded-full ${cfg.dot} animate-pulse`}
        aria-hidden="true"
      />
      {cfg.label}
      {score !== undefined && (
        <span className="opacity-60 font-normal tabular-nums">
          ({score > 0 ? "+" : ""}{score})
        </span>
      )}
    </div>
  );
}
