import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import type { SkinConditionCode, SeverityLevel } from "./api";
import { CLASS_LABELS, CLASS_SEVERITY } from "./constants";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

// ── Tailwind helper ────────────────────────────────────────────

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// ── Number formatting ──────────────────────────────────────────

/** Format 0.856 → "85.6%" */
export function formatPercent(value: number, decimals = 1): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

/** Format 0.856 → "85.6" (no % symbol) */
export function formatPercentValue(value: number, decimals = 1): string {
  return (value * 100).toFixed(decimals);
}

// ── Class helpers ──────────────────────────────────────────────

export function getClassLabel(code: string): string {
  return CLASS_LABELS[code as SkinConditionCode] ?? code.toUpperCase();
}

export function getSeverityLevel(code: string): SeverityLevel {
  return CLASS_SEVERITY[code as SkinConditionCode] ?? "monitor";
}

/** Returns Tailwind color classes for a severity level */
export function getSeverityColor(level: SeverityLevel): {
  text: string;
  bg: string;
  border: string;
  badge: string;
} {
  switch (level) {
    case "benign":
      return {
        text: "text-emerald-400",
        bg: "bg-emerald-500/10",
        border: "border-emerald-500/30",
        badge: "bg-emerald-500/20 text-emerald-400",
      };
    case "monitor":
      return {
        text: "text-amber-400",
        bg: "bg-amber-500/10",
        border: "border-amber-500/30",
        badge: "bg-amber-500/20 text-amber-400",
      };
    case "urgent":
      return {
        text: "text-red-400",
        bg: "bg-red-500/10",
        border: "border-red-500/30",
        badge: "bg-red-500/20 text-red-400",
      };
  }
}

/** Returns Tailwind text color class for confidence value (0-1) */
export function getConfidenceColorClass(confidence: number): string {
  if (confidence >= 0.8) return "text-emerald-400";
  if (confidence >= 0.6) return "text-amber-400";
  return "text-red-400";
}

// ── API ────────────────────────────────────────────────────────

/** Call FastAPI /predict with a data URL image (legacy support) */
export async function predictImage(imageData: string) {
  const imageBlob = await fetch(imageData).then((res) => res.blob());
  const formData = new FormData();
  formData.append("file", imageBlob, "upload.png");

  const response = await fetch(
    `${API_BASE_URL}/predict?include_gradcam=true`,
    { method: "POST", body: formData }
  );

  if (!response.ok) {
    throw new Error(`Prediction failed with status ${response.status}`);
  }

  return response.json();
}

// ── File helpers ───────────────────────────────────────────────

export function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      const result = reader.result as string;
      resolve(result.split(",")[1]); // Strip data URL prefix
    };
    reader.onerror = reject;
  });
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// ── Confidence helpers ─────────────────────────────────────────

/** Legacy color helper kept for backward compatibility */
export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return "text-green-400";
  if (confidence >= 0.6) return "text-yellow-400";
  return "text-red-400";
}