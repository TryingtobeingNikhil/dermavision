"""
DermaVision — Pydantic Schemas.

Request and response models for the API endpoints.
"""

from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    """Response model for /predict endpoint."""

    predicted_class: str = Field(
        ...,
        description="Predicted class abbreviation",
        examples=["mel"],
    )
    class_name: str = Field(
        ...,
        description="Full class name",
        examples=["Melanoma"],
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Calibrated prediction confidence score",
        examples=[0.89],
    )
    probabilities: dict[str, float] = Field(
        ...,
        description="Per-class probabilities",
    )
    is_malignant: bool = Field(
        ...,
        description="Whether the predicted condition is malignant",
    )
    severity: str = Field(
        ...,
        description="Severity level (low, high, critical)",
        examples=["critical"],
    )
    is_uncertain: bool = Field(
        ...,
        description="True if confidence < 0.60 threshold",
    )
    uncertainty_message: str = Field(
        ...,
        description="Human-readable uncertainty status",
        examples=["✅ Prediction confident."],
    )


class HealthResponse(BaseModel):
    """Response model for /health endpoint."""

    status: str = Field(..., examples=["healthy"])
    model_loaded: bool = Field(...)
    version: str = Field(..., examples=["1.0.0"])


class ModelInfoResponse(BaseModel):
    """Response model for /model-info endpoint."""

    architecture: str = Field(..., examples=["EfficientNet-B3"])
    num_classes: int = Field(..., examples=[7])
    input_size: int = Field(..., examples=[224])
    classes: list[str] = Field(
        ...,
        description="List of supported diagnostic classes",
    )
    total_parameters: int = Field(...)


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Detailed error info")
