"""
FastAPI backend for skin lesion classification.

Endpoints:
- POST /predict - Upload image, get prediction
- GET /health - Health check
- GET /model-info - Model metadata
"""

from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import numpy as np
from PIL import Image
import io
import base64
import torch

from ml.src.inference.predictor import SkinLesionPredictor

# Initialize FastAPI
app = FastAPI(
    title="DermaVision API",
    description="AI-powered skin lesion classification with uncertainty detection",
    version="1.0.0"
)

# CORS middleware (allow frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global predictor instance
predictor = None


@app.on_event("startup")
async def startup_event():
    """Load model on startup."""
    global predictor
    
    # Auto-detect device
    if torch.backends.mps.is_available():
        device = 'mps'
    elif torch.cuda.is_available():
        device = 'cuda'
    else:
        device = 'cpu'
    
    # Initialize predictor with model under ml/models
    model_path = repo_root / "ml" / "models" / "best_model.pth"
    predictor = SkinLesionPredictor(
        model_path=str(model_path),
        device=device,
        confidence_threshold=0.60
    )
    
    print(f"Model loaded on {device}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "DermaVision API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/predict (POST)",
            "health": "/health (GET)",
            "model_info": "/model-info (GET)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    
    is_healthy = predictor is not None
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "model_loaded": is_healthy,
        "device": predictor.device if is_healthy else None
    }


@app.get("/model-info")
async def model_info():
    """Get model information."""
    
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_name": "DermaVision-EfficientNet-B3",
        "version": "1.0.0",
        "classes": list(predictor.class_names.values()),
        "num_classes": len(predictor.class_names),
        "uncertainty_threshold": predictor.confidence_threshold,
        "device": predictor.device,
        "description": "Skin lesion classification with clinical-grade uncertainty detection"
    }


@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    include_gradcam: bool = True
):
    """
    Predict skin lesion class from uploaded image.
    
    Args:
        file: Image file (JPG, PNG)
        include_gradcam: Include Grad-CAM visualization
        
    Returns:
        Prediction results with optional Grad-CAM overlay
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an image (JPG, PNG, etc.)"
        )
    
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        
        # Save temporarily
        temp_path = Path("temp_upload.jpg")
        image.save(temp_path)
        
        # Make prediction
        if include_gradcam:
            result = predictor.predict_with_gradcam(str(temp_path))
            
            # Convert Grad-CAM overlay to base64
            gradcam_image = Image.fromarray(result['gradcam_overlay'])
            buffered = io.BytesIO()
            gradcam_image.save(buffered, format="PNG")
            gradcam_b64 = base64.b64encode(buffered.getvalue()).decode()
            
            result['gradcam_base64'] = gradcam_b64
            
            # Remove numpy arrays from response
            del result['original_image']
            del result['gradcam_overlay']
        else:
            result = predictor.predict(str(temp_path))
        
        # Clean up temp file
        temp_path.unlink()
        
        return JSONResponse(content=result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# Optional: Batch prediction endpoint
@app.post("/predict-batch")
async def predict_batch(files: list[UploadFile] = File(...)):
    """
    Predict on multiple images.
    
    Args:
        files: List of image files
        
    Returns:
        List of predictions
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 images per batch"
        )
    
    results = []
    
    for i, file in enumerate(files):
        try:
            # Read and save
            contents = await file.read()
            image = Image.open(io.BytesIO(contents)).convert('RGB')
            temp_path = Path(f"temp_upload_{i}.jpg")
            image.save(temp_path)
            
            # Predict
            result = predictor.predict(str(temp_path))
            result['filename'] = file.filename
            
            results.append(result)
            
            # Clean up
            temp_path.unlink()
            
        except Exception as e:
            results.append({
                'filename': file.filename,
                'error': str(e)
            })
    
    return JSONResponse(content={"results": results})