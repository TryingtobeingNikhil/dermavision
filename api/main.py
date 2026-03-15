"""
DermaVision — FastAPI Application.

Production-ready REST API for skin lesion classification with
health monitoring and model information endpoints.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .endpoints import health, predict


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: load model on startup, cleanup on shutdown."""
    # Startup: load model
    predict.load_model()
    print("✅ DermaVision model loaded successfully")
    yield
    # Shutdown: cleanup
    print("👋 DermaVision API shutting down")


app = FastAPI(
    title="DermaVision API",
    description=(
        "AI-powered skin lesion classification API using EfficientNet-B3. "
        "Classifies dermatoscopic images into 7 diagnostic categories."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(predict.router, prefix="/predict", tags=["Prediction"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "DermaVision API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
