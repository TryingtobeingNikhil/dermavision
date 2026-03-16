// API Client - DermaVision

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

// ── Types ──────────────────────────────────────────────────────

export type SkinConditionCode =
  | "akiec"
  | "bcc"
  | "bkl"
  | "df"
  | "mel"
  | "nv"
  | "vasc";

export interface PredictionResponse {
  predicted_class: SkinConditionCode;
  confidence: number; // 0.0 to 1.0
  all_probabilities: Record<string, number>;
  high_uncertainty: boolean;
  gradcam_overlay?: string; // Base64-encoded PNG
}

// ── API Functions ──────────────────────────────────────────────

/**
 * Send an image File to the backend for skin lesion analysis.
 * The `include_gradcam=true` query param tells the API to return a Grad-CAM overlay.
 */
export async function analyzeSkinLesion(
  file: File
): Promise<PredictionResponse> {
  const formData = new FormData();
  formData.append("file", file);

  let response: Response;
  try {
    response = await fetch(
      `${API_BASE_URL}/predict?include_gradcam=true`,
      {
        method: "POST",
        body: formData,
        // Do NOT set Content-Type here; browser sets it with correct boundary
      }
    );
  } catch (err) {
    // Network / CORS error
    throw new ApiError("network", "Cannot reach the API server. Is the backend running?");
  }

  if (!response.ok) {
    if (response.status === 413) {
      throw new ApiError("file_too_large", "Image too large. Max size is 10 MB.");
    }
    if (response.status === 415) {
      throw new ApiError("unsupported_type", "Unsupported image type. Please upload JPG or PNG.");
    }
    if (response.status >= 500) {
      throw new ApiError("server", `Server error (${response.status}). Please try again.`);
    }
    throw new ApiError("unknown", `Request failed with status ${response.status}.`);
  }

  const data = await response.json();

  // Reverse mapping for all_probabilities names -> codes
  const NAME_TO_CODE: Record<string, SkinConditionCode> = {
    "Actinic keratoses": "akiec",
    "Basal cell carcinoma": "bcc",
    "Benign keratosis-like lesions": "bkl", // The backend might use this or "Benign keratosis"
    "Dermatofibroma": "df",
    "Melanoma": "mel",
    "Melanocytic nevi": "nv",
    "Vascular lesions": "vasc"
  };

  // The backend might return slightly different names, let's just make sure we map it!
  const allProbs: Record<string, number> = {};
  if (data.all_probabilities) {
    for (const [name, prob] of Object.entries(data.all_probabilities)) {
      const code = NAME_TO_CODE[name] || name;
      allProbs[code as string] = prob as number;
    }
  }

  // Map the backend payload to the expected frontend format
  return {
    predicted_class: data.predicted_class_code,
    confidence: data.confidence,
    all_probabilities: allProbs,
    high_uncertainty: data.uncertain ?? false,
    gradcam_overlay: data.gradcam_base64
  } as PredictionResponse;
}

/**
 * Overload that accepts a data-URL string (used by the existing ImageUploader logic).
 */
export async function analyzeSkinLesionFromDataUrl(
  dataUrl: string
): Promise<PredictionResponse> {
  const blob = await fetch(dataUrl).then((r) => r.blob());
  const file = new File([blob], "upload.jpg", { type: blob.type || "image/jpeg" });
  return analyzeSkinLesion(file);
}

// ── Error class ────────────────────────────────────────────────

export type ApiErrorCode =
  | "network"
  | "file_too_large"
  | "unsupported_type"
  | "server"
  | "unknown";

export class ApiError extends Error {
  constructor(
    public readonly code: ApiErrorCode,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}
