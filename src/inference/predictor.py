"""
DermaVision — Single Image Inference with Uncertainty.

Inference pipeline per design spec:
  1. Preprocess: Resize to 224x224, normalize (ImageNet stats)
  2. Model forward pass
  3. Softmax → raw probabilities
  4. Temperature scaling (calibration)
  5. Decision logic:
     - confidence >= 0.60 → return prediction
     - confidence < 0.60  → "Uncertain — Seek dermatologist"
  6. Optional: Grad-CAM heatmap
"""

import json

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

from ..data.augmentations import get_val_transforms
from ..models.cnn_model import DermaModel

# Default confidence threshold per design spec
CONFIDENCE_THRESHOLD = 0.60


class Predictor:
    """Single-image prediction engine with uncertainty estimation.

    Implements the full inference pipeline with confidence-based
    decision logic and optional temperature scaling.

    Args:
        model_path: Path to saved model checkpoint (.pth).
        class_mapping_path: Path to class_mapping.json.
        device: Inference device ('auto', 'cuda', 'cpu', 'mps').
        image_size: Input image size (224 per spec).
        confidence_threshold: Minimum confidence to accept prediction.
        temperature: Temperature for calibration (None = no scaling).

    Example:
        >>> predictor = Predictor("models/best_model.pth")
        >>> result = predictor.predict("path/to/image.jpg")
        >>> if result['is_uncertain']:
        ...     print("⚠️ Uncertain — Seek dermatologist")
    """

    def __init__(
        self,
        model_path: str = "models/best_model.pth",
        class_mapping_path: str = "config/class_mapping.json",
        device: str = "auto",
        image_size: int = 224,
        confidence_threshold: float = CONFIDENCE_THRESHOLD,
        temperature: float | None = None,
    ):
        # Device selection
        if device == "auto":
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
            elif torch.backends.mps.is_available():
                self.device = torch.device("mps")
            else:
                self.device = torch.device("cpu")
        else:
            self.device = torch.device(device)

        self.confidence_threshold = confidence_threshold
        self.temperature = temperature

        # Load class mapping
        with open(class_mapping_path, "r") as f:
            self.class_mapping = json.load(f)

        self.idx_to_class = self.class_mapping["idx_to_class"]
        self.classes = self.class_mapping["classes"]

        # Load model
        self.model = self._load_model(model_path)
        self.model.eval()

        # Preprocessing: Resize to 224x224 + normalize (ImageNet stats)
        self.transform = get_val_transforms(image_size)

    def _load_model(self, model_path: str) -> DermaModel:
        """Load model from checkpoint."""
        checkpoint = torch.load(model_path, map_location=self.device)

        num_classes = checkpoint.get("config", {}).get("num_classes", 7)
        model = DermaModel(num_classes=num_classes, pretrained=False)
        model.load_state_dict(checkpoint["model_state_dict"])
        model.to(self.device)

        # Extract temperature if saved during calibration
        if self.temperature is None and "temperature" in checkpoint:
            self.temperature = checkpoint["temperature"]

        return model

    @torch.no_grad()
    def predict(self, image_path: str) -> dict:
        """Run the full inference pipeline on a single image.

        Pipeline:
          1. Image preprocessing (224x224, ImageNet normalize)
          2. Model forward pass
          3. Softmax → raw probabilities
          4. Temperature scaling (if calibrated)
          5. Confidence check → uncertain flag

        Args:
            image_path: Path to the input image.

        Returns:
            Dictionary with:
                - predicted_class: Class abbreviation
                - class_name: Full class name
                - confidence: Calibrated confidence (0-1)
                - probabilities: All class probabilities
                - is_malignant: Whether the predicted class is malignant
                - severity: Severity level
                - is_uncertain: True if confidence < threshold
                - uncertainty_message: Human-readable uncertainty note
        """
        # Step 1: Preprocess — resize to 224x224 + normalize
        image = np.array(Image.open(image_path).convert("RGB"))
        transformed = self.transform(image=image)
        input_tensor = transformed["image"].unsqueeze(0).to(self.device)

        # Step 2: Model forward pass
        logits = self.model(input_tensor)

        # Step 3 & 4: Softmax with optional temperature scaling
        if self.temperature and self.temperature != 1.0:
            scaled_logits = logits / self.temperature
        else:
            scaled_logits = logits

        probabilities = F.softmax(scaled_logits, dim=1).squeeze().cpu().numpy()

        # Step 5: Decision logic
        pred_idx = int(np.argmax(probabilities))
        confidence = float(probabilities[pred_idx])
        pred_class = self.idx_to_class[str(pred_idx)]
        class_info = self.classes[str(pred_idx)]

        is_uncertain = confidence < self.confidence_threshold

        if is_uncertain:
            uncertainty_message = (
                "⚠️ Uncertain — Confidence below threshold. "
                "Please seek evaluation from a dermatologist."
            )
        else:
            uncertainty_message = "✅ Prediction confident."

        return {
            "predicted_class": pred_class,
            "class_name": class_info["name"],
            "confidence": confidence,
            "probabilities": {
                self.idx_to_class[str(i)]: float(p)
                for i, p in enumerate(probabilities)
            },
            "is_malignant": class_info["malignant"],
            "severity": class_info["severity"],
            "is_uncertain": is_uncertain,
            "uncertainty_message": uncertainty_message,
        }

    @torch.no_grad()
    def predict_batch(self, image_paths: list[str]) -> list[dict]:
        """Make predictions on multiple images.

        Args:
            image_paths: List of image file paths.

        Returns:
            List of prediction dictionaries.
        """
        return [self.predict(path) for path in image_paths]
