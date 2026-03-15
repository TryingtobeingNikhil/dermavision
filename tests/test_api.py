"""
DermaVision — API Tests.

Tests for FastAPI endpoints using httpx test client.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from api.main import app
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_200(self, client):
        """Verify health endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_schema(self, client):
        """Verify health response contains required fields."""
        response = client.get("/health")
        data = response.json()

        assert "status" in data
        assert "model_loaded" in data
        assert "version" in data

    def test_health_status_healthy(self, client):
        """Verify health status is 'healthy'."""
        response = client.get("/health")
        assert response.json()["status"] == "healthy"


class TestRootEndpoint:
    """Tests for the root / endpoint."""

    def test_root_returns_200(self, client):
        """Verify root endpoint returns 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_contains_service_name(self, client):
        """Verify root response contains service name."""
        response = client.get("/")
        data = response.json()
        assert "service" in data
        assert "DermaVision" in data["service"]


class TestPredictEndpoint:
    """Tests for the /predict endpoint."""

    def test_predict_rejects_non_image(self, client):
        """Verify predict endpoint rejects non-image files."""
        response = client.post(
            "/predict/",
            files={"file": ("test.txt", b"not an image", "text/plain")},
        )
        assert response.status_code == 400 or response.status_code == 503

    def test_predict_requires_file(self, client):
        """Verify predict endpoint requires a file upload."""
        response = client.post("/predict/")
        assert response.status_code == 422  # Validation error
