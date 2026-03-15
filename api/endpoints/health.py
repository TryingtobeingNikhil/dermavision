"""
DermaVision — Health & Model Info Endpoints.

Provides system health checks and model information for monitoring.
"""

from fastapi import APIRouter

from ..schemas import HealthResponse, ModelInfoResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check if the API and model are running correctly.",
)
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    from .predict import _predictor

    return HealthResponse(
        status="healthy",
        model_loaded=_predictor is not None,
        version="1.0.0",
    )


@router.get(
    "/model-info",
    response_model=ModelInfoResponse,
    summary="Model information",
    description="Get details about the loaded model.",
)
async def model_info():
    """Return model architecture and configuration details."""
    from .predict import _predictor

    if _predictor is None:
        return ModelInfoResponse(
            architecture="EfficientNet-B3",
            num_classes=7,
            input_size=300,
            classes=["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"],
            total_parameters=0,
        )

    from src.training.utils import count_parameters

    params = count_parameters(_predictor.model)

    return ModelInfoResponse(
        architecture="EfficientNet-B3",
        num_classes=7,
        input_size=300,
        classes=list(_predictor.idx_to_class.values()),
        total_parameters=params["total"],
    )
