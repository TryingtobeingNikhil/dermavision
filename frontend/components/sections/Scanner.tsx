"use client";

import { useState, useCallback, useRef } from "react";
import {
  Upload, Loader2, AlertTriangle, Eye, EyeOff,
  X, Sparkles, RotateCcw,
} from "lucide-react";
import { cn, formatPercent, getClassLabel, getSeverityLevel, getSeverityColor } from "@/lib/utils";
import { analyzeSkinLesion, type PredictionResponse } from "@/lib/api";
import { ALLOWED_MIME_TYPES, MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB, CLASS_DESCRIPTIONS } from "@/lib/constants";
import type { SkinConditionCode } from "@/lib/api";

// ── State machine ──────────────────────────────────────────────
type ScannerState = "idle" | "uploaded" | "analyzing" | "results" | "error";

export function Scanner() {
  const [state, setState] = useState<ScannerState>("idle");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showGradCAM, setShowGradCAM] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // ── File validation ────────────────────────────────────────

  const validateFile = useCallback((file: File): string | null => {
    if (!ALLOWED_MIME_TYPES.includes(file.type as any)) {
      return "Invalid file type. Please upload a JPG or PNG image.";
    }
    if (file.size > MAX_FILE_SIZE_BYTES) {
      return `File too large. Maximum size is ${MAX_FILE_SIZE_MB} MB.`;
    }
    return null;
  }, []);

  // ── File selection ─────────────────────────────────────────

  const handleFileSelect = useCallback(
    (file: File) => {
      const validationError = validateFile(file);
      if (validationError) {
        setError(validationError);
        setState("error");
        return;
      }

      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      setError(null);
      setResult(null);
      setShowGradCAM(false);
      setState("uploaded");
    },
    [validateFile]
  );

  // ── Drag and drop ──────────────────────────────────────────

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFileSelect(file);
    },
    [handleFileSelect]
  );

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFileSelect(file);
    },
    [handleFileSelect]
  );

  // ── Analysis ───────────────────────────────────────────────

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setState("analyzing");
    setError(null);

    try {
      const data = await analyzeSkinLesion(selectedFile);
      setResult(data);
      setState("results");
    } catch (err: any) {
      setError(err?.message || "Analysis failed. Please try again.");
      setState("error");
    }
  };

  // ── Reset ──────────────────────────────────────────────────

  const handleReset = () => {
    if (preview) URL.revokeObjectURL(preview);
    setSelectedFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    setShowGradCAM(false);
    setState("idle");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // ── Render ─────────────────────────────────────────────────

  return (
    <section id="scanner" className="relative py-24" aria-label="Skin lesion scanner">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-12">
          <span className="text-sm font-medium text-cyan-400 tracking-wider uppercase mb-3 block">
            Demo
          </span>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-display font-bold mb-4">
            Try the{" "}
            <span className="gradient-text">Scanner</span>
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Upload a dermatoscopic image to get instant AI-powered classification
          </p>
        </div>

        {/* ── Upload zone ── */}
        {(state === "idle" || state === "error") && (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={cn(
              "glass-card p-10 sm:p-14 rounded-2xl",
              "border-2 border-dashed transition-all duration-300",
              isDragging
                ? "border-cyan-400 bg-cyan-400/5 shadow-glow scale-[1.02]"
                : "border-slate-700/60 hover:border-cyan-400/40",
            )}
          >
            <label className="block cursor-pointer text-center">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/jpg,image/png"
                onChange={handleInputChange}
                className="sr-only"
                aria-label="Upload skin lesion image"
              />

              <div className="mb-6">
                <div className={cn(
                  "w-20 h-20 mx-auto rounded-2xl flex items-center justify-center",
                  "bg-gradient-to-br from-blue-500/20 to-cyan-400/20",
                  "text-cyan-400 transition-all duration-500",
                  isDragging && "scale-110 shadow-glow"
                )}>
                  <Upload className="w-10 h-10" />
                </div>
              </div>

              <p className="text-xl font-display font-semibold text-slate-200 mb-2">
                Drop your image here
              </p>
              <p className="text-slate-400 mb-6">or click to browse</p>

              <span className={cn(
                "inline-flex items-center gap-2 px-6 py-3 rounded-xl",
                "bg-gradient-to-r from-blue-500 to-cyan-400 text-white font-semibold",
                "shadow-glow hover:shadow-glow-strong hover:scale-105 active:scale-95",
                "transition-all duration-300"
              )}>
                <Sparkles className="w-4 h-4" />
                Select Image
              </span>

              <p className="text-xs text-slate-500 mt-6">
                JPG, JPEG, PNG — up to {MAX_FILE_SIZE_MB} MB
              </p>
            </label>

            {/* Error display in upload zone */}
            {error && state === "error" && (
              <div className="mt-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-center gap-3">
                <AlertTriangle className="w-5 h-5 text-red-400 shrink-0" />
                <p className="text-sm text-red-400">{error}</p>
                <button
                  onClick={(e) => { e.preventDefault(); setError(null); setState("idle"); }}
                  className="ml-auto text-red-400 hover:text-red-300 transition-colors"
                  aria-label="Dismiss error"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        )}

        {/* ── Preview + analyse ── */}
        {(state === "uploaded" || state === "analyzing") && preview && (
          <div className="glass-card p-6 sm:p-8 rounded-2xl space-y-6">
            {/* Image preview */}
            <div className="relative rounded-xl overflow-hidden bg-slate-900">
              <img
                src={preview}
                alt="Uploaded skin lesion"
                className="w-full h-auto max-h-[400px] object-contain mx-auto"
              />

              {/* Scanning overlay */}
              {state === "analyzing" && (
                <div className="absolute inset-0 bg-slate-950/60 flex flex-col items-center justify-center">
                  {/* Scan line */}
                  <div className="absolute inset-x-0 h-0.5 bg-gradient-to-r from-transparent via-cyan-400 to-transparent animate-scanner-sweep" aria-hidden="true" />
                  <Loader2 className="w-10 h-10 animate-spin text-cyan-400 mb-3" />
                  <p className="text-sm text-slate-300 font-medium" role="status" aria-live="polite">
                    Analyzing image…
                  </p>
                </div>
              )}
            </div>

            {/* Action buttons */}
            <div className="flex gap-3">
              <button
                onClick={handleAnalyze}
                disabled={state === "analyzing"}
                className={cn(
                  "flex-1 px-6 py-3.5 rounded-xl font-semibold",
                  "bg-gradient-to-r from-blue-500 to-cyan-400 text-white",
                  "shadow-glow hover:shadow-glow-strong hover:scale-[1.02]",
                  "active:scale-[0.98] transition-all duration-300",
                  "disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100",
                  "focus-ring inline-flex items-center justify-center gap-2"
                )}
              >
                {state === "analyzing" ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Analyzing…
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Analyze
                  </>
                )}
              </button>

              <button
                onClick={handleReset}
                disabled={state === "analyzing"}
                className={cn(
                  "px-6 py-3.5 rounded-xl font-semibold glass-card",
                  "text-slate-300 hover:text-cyan-400 hover:border-cyan-400/30",
                  "transition-all duration-300 focus-ring",
                  "inline-flex items-center gap-2",
                  "disabled:opacity-50 disabled:cursor-not-allowed"
                )}
              >
                <RotateCcw className="w-4 h-4" />
                Clear
              </button>
            </div>
          </div>
        )}

        {/* ── Results ── */}
        {state === "results" && result && (
          <div className="space-y-6">
            {/* New scan button */}
            <div className="flex justify-end">
              <button
                onClick={handleReset}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-slate-400 hover:text-cyan-400 hover:bg-white/5 transition-all focus-ring"
              >
                <RotateCcw className="w-4 h-4" />
                New Scan
              </button>
            </div>

            {/* Primary result card */}
            <ResultCard result={result} preview={preview} />

            {/* Uncertainty warning */}
            {result.high_uncertainty && (
              <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-semibold text-amber-400 mb-1">High Uncertainty Detected</p>
                  <p className="text-sm text-amber-400/80">
                    The AI model is not confident in this prediction. Please consult a qualified dermatologist for professional evaluation.
                  </p>
                </div>
              </div>
            )}

            {/* All probabilities */}
            <ProbabilitiesCard probabilities={result.all_probabilities} predicted={result.predicted_class} />

            {/* Grad-CAM */}
            {result.gradcam_overlay && (
              <GradCAMCard
                overlay={result.gradcam_overlay}
                show={showGradCAM}
                onToggle={() => setShowGradCAM(!showGradCAM)}
              />
            )}
          </div>
        )}
      </div>
    </section>
  );
}

// ================================================================
// Sub-components
// ================================================================

function ResultCard({ result, preview }: { result: PredictionResponse; preview: string | null }) {
  const severity = getSeverityLevel(result.predicted_class);
  const colors = getSeverityColor(severity);
  const confidencePct = result.confidence * 100;

  return (
    <div className="glass-card p-6 sm:p-8 rounded-2xl">
      <div className="flex flex-col sm:flex-row sm:items-start gap-6">
        {/* Thumbnail */}
        {preview && (
          <div className="w-24 h-24 rounded-xl overflow-hidden shrink-0 border border-white/10">
            <img src={preview} alt="Analyzed lesion" className="w-full h-full object-cover" />
          </div>
        )}

        {/* Details */}
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-3 mb-2">
            <h3 className="text-2xl font-display font-bold gradient-text">
              {getClassLabel(result.predicted_class)}
            </h3>
            <span className={cn("px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider", colors.badge)}>
              {severity}
            </span>
          </div>

          <p className="text-sm text-slate-400 mb-4">
            {CLASS_DESCRIPTIONS[result.predicted_class as SkinConditionCode] ?? ""}
          </p>

          {/* Confidence bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Confidence</span>
              <span className="font-mono font-semibold text-slate-200">
                {formatPercent(result.confidence)}
              </span>
            </div>
            <div className="h-2.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-400 transition-all duration-1000 ease-out"
                style={{ width: `${confidencePct}%` }}
                role="progressbar"
                aria-valuenow={Math.round(confidencePct)}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label={`Confidence: ${formatPercent(result.confidence)}`}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ProbabilitiesCard({
  probabilities,
  predicted,
}: {
  probabilities: Record<string, number>;
  predicted: string;
}) {
  const sorted = Object.entries(probabilities).sort(([, a], [, b]) => b - a);

  return (
    <div className="glass-card p-6 sm:p-8 rounded-2xl">
      <h4 className="font-display font-semibold text-slate-100 mb-5">
        All Predictions
      </h4>
      <div className="space-y-4">
        {sorted.map(([code, prob]) => {
          const isPredicted = code === predicted;
          return (
            <div key={code} className="space-y-1.5">
              <div className="flex items-center justify-between text-sm">
                <span className={cn("font-medium", isPredicted ? "text-cyan-400" : "text-slate-300")}>
                  {getClassLabel(code)}
                  {isPredicted && (
                    <span className="ml-2 text-xs text-cyan-400/60">← predicted</span>
                  )}
                </span>
                <span className="font-mono text-sm text-slate-400">
                  {formatPercent(prob)}
                </span>
              </div>
              <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className={cn(
                    "h-full rounded-full transition-all duration-700 ease-out",
                    isPredicted
                      ? "bg-gradient-to-r from-blue-500 to-cyan-400"
                      : "bg-slate-600"
                  )}
                  style={{ width: `${Math.max(prob * 100, 0.5)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function GradCAMCard({
  overlay,
  show,
  onToggle,
}: {
  overlay: string;
  show: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="glass-card p-6 sm:p-8 rounded-2xl">
      <div className="flex items-center justify-between mb-4">
        <h4 className="font-display font-semibold text-slate-100">
          Grad-CAM Visualization
        </h4>
        <button
          onClick={onToggle}
          className="inline-flex items-center gap-2 text-sm text-cyan-400 hover:text-cyan-300 transition-colors focus-ring rounded-lg px-3 py-1.5"
          aria-expanded={show}
          aria-controls="gradcam-image"
        >
          {show ? (
            <>
              <EyeOff className="w-4 h-4" /> Hide
            </>
          ) : (
            <>
              <Eye className="w-4 h-4" /> Show
            </>
          )}
        </button>
      </div>

      {show && (
        <div id="gradcam-image" className="space-y-3">
          <div className="rounded-xl overflow-hidden border border-white/10">
            <img
              src={`data:image/png;base64,${overlay}`}
              alt="Grad-CAM heatmap highlighting regions of focus for the AI diagnosis"
              className="w-full h-auto"
            />
          </div>
          <p className="text-xs text-slate-500">
            The heatmap highlights regions that most influenced the AI&apos;s decision. Warmer colours indicate higher activation.
          </p>
        </div>
      )}
    </div>
  );
}
