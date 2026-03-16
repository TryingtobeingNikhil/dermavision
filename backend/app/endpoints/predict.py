"""
DermaVision — Prediction Endpoint.

Handles image upload and returns classification results.
"""

import io
import tempfile
from pathlib import Path

import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image

from ..schemas import ErrorResponse, PredictionResponse

router = APIRouter()

# Global predictor instance (loaded at startup)
_predictor = None


def load_model(
    model_path: str | None = None,
    class_mapping_path: str | None = None,
) -> None:
    """Load the prediction model at application startup."""
    global _predictor
    try:
        repo_root = Path(__file__).resolve().parents[3]
        default_model_path = repo_root / "ml" / "models" / "best_model.pth"
        model_path = Path(model_path) if model_path is not None else default_model_path

        from ml.src.inference.predictor import SkinLesionPredictor

        _predictor = SkinLesionPredictor(
            model_path=str(model_path),
            device="cpu",
            confidence_threshold=0.60,
        )
    except Exception as e:
        print(f"⚠️  Model loading failed: {e}")
        print("   API will run without model (predictions unavailable)")


@router.post(
    "/",
    response_model=PredictionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Classify a skin lesion image",
    description="Upload a dermatoscopic image for skin lesion classification.",
)
async def predict_image(
    file: UploadFile = File(..., description="Skin lesion image (JPEG/PNG)"),
):
    """Classify an uploaded skin lesion image.

    Accepts JPEG or PNG images. Returns the predicted diagnosis,
    confidence score, and per-class probabilities.
    """
    if _predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Ensure model weights exist at models/best_model.pth",
        )

    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Expected JPEG or PNG.",
        )

    try:
        # Read and validate image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        # Save to temp file for predictor
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            image.save(tmp.name)
            result = _predictor.predict(tmp.name)

        return PredictionResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}",
        )
