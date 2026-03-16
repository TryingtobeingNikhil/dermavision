"""Test FastAPI endpoints."""

import requests
from pathlib import Path
import json

# API base URL
BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_model_info():
    """Test model info endpoint."""
    print("Testing /model-info endpoint...")
    response = requests.get(f"{BASE_URL}/model-info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_predict():
    """Test prediction endpoint."""
    print("Testing /predict endpoint...")
    
    # Find a test image
    test_image = Path("data/processed/HAM10000_images_part_1").glob("*.jpg").__next__()
    
    # Upload
    with open(test_image, 'rb') as f:
        files = {'file': (test_image.name, f, 'image/jpeg')}
        response = requests.post(
            f"{BASE_URL}/predict",
            files=files,
            params={'include_gradcam': True}
        )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Prediction: {result['prediction']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Uncertain: {result['uncertain']}")
        print(f"Grad-CAM included: {'gradcam_base64' in result}")
    else:
        print(f"Error: {response.text}")
    
    print()


if __name__ == '__main__':
    print("="*60)
    print("Testing DermaVision API")
    print("="*60)
    print()
    
    test_health()
    test_model_info()
    test_predict()
    
    print("All API tests complete!")