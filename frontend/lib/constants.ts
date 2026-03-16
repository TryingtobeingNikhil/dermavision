// ================================================================
// App-wide Constants — DermaVision
// ================================================================

import type { SkinConditionCode } from "./api";

// ── Class Labels ───────────────────────────────────────────────

export const CLASS_LABELS: Record<SkinConditionCode, string> = {
  akiec: "Actinic Keratoses",
  bcc: "Basal Cell Carcinoma",
  bkl: "Benign Keratosis",
  df: "Dermatofibroma",
  mel: "Melanoma",
  nv: "Melanocytic Nevi",
  vasc: "Vascular Lesions",
};

export const CLASS_DESCRIPTIONS: Record<SkinConditionCode, string> = {
  akiec: "Pre-cancerous skin lesion caused by sun damage",
  bcc: "Most common form of skin cancer, usually treatable",
  bkl: "Non-cancerous growth from keratinization of skin cells",
  df: "Benign fibrous nodule, most common on lower legs",
  mel: "Most dangerous form of skin cancer, requires urgent attention",
  nv: "Common moles — usually benign, monitor for changes",
  vasc: "Blood vessel-related skin lesions, generally benign",
};

export type SeverityLevel = "benign" | "monitor" | "urgent";

export const CLASS_SEVERITY: Record<SkinConditionCode, SeverityLevel> = {
  nv: "benign",
  bkl: "benign",
  df: "benign",
  vasc: "benign",
  akiec: "monitor",
  bcc: "monitor",
  mel: "urgent",
};

// ── Navigation ─────────────────────────────────────────────────

export const NAV_LINKS = [
  { label: "Demo", href: "#scanner" },
  { label: "How It Works", href: "#how-it-works" },
  { label: "Features", href: "#features" },
  { label: "About", href: "#about" },
] as const;

// ── Stats ──────────────────────────────────────────────────────

export const STATS = [
  {
    id: "accuracy",
    value: "85.6%",
    label: "Train Accuracy",
    icon: "TrendingUp",
    description: "On HAM10000 test set",
  },
  {
    id: "sensitivity",
    value: "87.4%",
    label: "Melanoma Sensitivity",
    icon: "ShieldCheck",
    description: "Early detection rate",
  },
  {
    id: "dataset",
    value: "10,015",
    label: "Training Images",
    icon: "Database",
    description: "HAM10000 dermatoscopic images",
  },
  {
    id: "inference",
    value: "<2s",
    label: "Avg Inference",
    icon: "Zap",
    description: "Real-time predictions",
  },
] as const;

// ── Features ───────────────────────────────────────────────────

export const FEATURES = [
  {
    id: "efficientnet",
    icon: "Cpu",
    title: "EfficientNet-B3 Backbone",
    description: "State-of-the-art neural network architecture optimised for medical imaging",
    gradient: "from-blue-500/20 to-cyan-500/20",
  },
  {
    id: "focal-loss",
    icon: "Target",
    title: "Focal Loss Training",
    description: "Handles severe class imbalance for detecting rare skin conditions",
    gradient: "from-cyan-500/20 to-teal-500/20",
  },
  {
    id: "gradcam",
    icon: "Eye",
    title: "Grad-CAM Explainability",
    description: "Visual heatmaps highlight the exact regions driving AI decisions",
    gradient: "from-teal-500/20 to-green-500/20",
  },
  {
    id: "calibration",
    icon: "Gauge",
    title: "Confidence Calibration",
    description: "Reliable, well-calibrated probability estimates with uncertainty flags",
    gradient: "from-violet-500/20 to-blue-500/20",
  },
  {
    id: "ham10000",
    icon: "Database",
    title: "HAM10000 Dataset",
    description: "Trained on 10,015 expert-annotated dermatoscopic images",
    gradient: "from-blue-500/20 to-indigo-500/20",
  },
  {
    id: "realtime",
    icon: "Zap",
    title: "Real-time Inference",
    description: "Sub-2-second predictions optimised for clinical workflow speed",
    gradient: "from-amber-500/20 to-orange-500/20",
  },
  {
    id: "augmentation",
    icon: "Sparkles",
    title: "Advanced Augmentation",
    description: "Robust to variations in lighting, angle, and image quality",
    gradient: "from-pink-500/20 to-rose-500/20",
  },
  {
    id: "api",
    icon: "Server",
    title: "Production REST API",
    description: "FastAPI backend ready for integration into healthcare systems",
    gradient: "from-emerald-500/20 to-teal-500/20",
  },
] as const;

// ── How It Works ───────────────────────────────────────────────

export const HOW_IT_WORKS_STEPS = [
  {
    number: "01",
    icon: "Upload",
    title: "Upload Image",
    description: "Drag & drop or click to upload a clear photo of the skin lesion (JPG/PNG, max 10 MB)",
  },
  {
    number: "02",
    icon: "Brain",
    title: "AI Processing",
    description: "EfficientNet-B3 extracts deep features and classifies the lesion across 7 conditions",
  },
  {
    number: "03",
    icon: "ScanSearch",
    title: "Grad-CAM Analysis",
    description: "Visual explanation heatmap generated to highlight areas that influenced the AI decision",
  },
  {
    number: "04",
    icon: "CheckCircle",
    title: "Get Results",
    description: "Detailed diagnosis with confidence scores, probability breakdown, and visual heatmap",
  },
] as const;

// ── File Validation ────────────────────────────────────────────

export const ALLOWED_MIME_TYPES = ["image/jpeg", "image/jpg", "image/png"] as const;
export const MAX_FILE_SIZE_MB = 10;
export const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

// ── Footer Links ───────────────────────────────────────────────

export const FOOTER_LINKS = {
  Product: [
    { label: "Demo Scanner", href: "#scanner" },
    { label: "How It Works", href: "#how-it-works" },
    { label: "Features", href: "#features" },
  ],
  Resources: [
    { label: "HAM10000 Dataset", href: "https://www.kaggle.com/kmader/skin-lesion-analysis-toward-melanoma-detection" },
    { label: "EfficientNet Paper", href: "https://arxiv.org/abs/1905.11946" },
    { label: "Grad-CAM Paper", href: "https://arxiv.org/abs/1610.02391" },
  ],
  Legal: [
    { label: "Not Medical Advice", href: "#disclaimer" },
    { label: "Privacy Policy", href: "#privacy" },
    { label: "Open Source", href: "https://github.com" },
  ],
} as const;
