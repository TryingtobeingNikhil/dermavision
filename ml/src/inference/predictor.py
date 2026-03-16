"""
Inference pipeline for single image predictions.

Handles:
- Image preprocessing
- Model inference
- Confidence calibration
- Uncertainty detection
- Result formatting
"""

import torch
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, Tuple, Optional
import cv2

from ml.src.models.cnn_model import SkinLesionClassifier
from ml.src.data.dataset import HAM10000Dataset
from ml.src.data.augmentations import get_valid_transforms


class SkinLesionPredictor:
    """
    Predictor for skin lesion classification with uncertainty detection.
    
    Features:
    - Single image inference
    - Confidence calibration via temperature scaling
    - 60% uncertainty threshold
    - Grad-CAM visualization (optional)
    """
    
    def __init__(
        self,
        model_path: str,
        device: str = 'cpu',
        confidence_threshold: float = 0.60
    ):
        """
        Initialize predictor.
        
        Args:
            model_path: Path to trained model checkpoint
            device: 'cpu', 'cuda', or 'mps'
            confidence_threshold: Minimum confidence for certain predictions
        """
        self.device = device
        self.confidence_threshold = confidence_threshold
        self.transform = get_valid_transforms(image_size=224)
        
        # Load model
        self.model = self._load_model(model_path)
        self.model.eval()
        
        # Class mappings
        self.idx_to_class = HAM10000Dataset.IDX_TO_CLASS
        self.class_names = HAM10000Dataset.FULL_NAMES
        
        print(f"✅ Predictor initialized")
        print(f"   Device: {device}")
        print(f"   Confidence threshold: {confidence_threshold}")
    
    def _load_model(self, model_path: str) -> SkinLesionClassifier:
        """Load trained model from checkpoint."""
        from ml.src.models.cnn_model import create_model
        
        # Create model architecture
        model = create_model(
            num_classes=7,
            pretrained=False,
            device=self.device
        )
        
        # Load weights
        # In PyTorch >=2.6, weights_only defaults to True which can break older checkpoints.
        # This checkpoint is created within this project and is trusted, so we opt into weights_only=False.
        checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
        model.load_state_dict(checkpoint['model_state_dict'])
        
        print(f"   Loaded from epoch {checkpoint.get('epoch', 'unknown')}")
        
        return model
    
    def preprocess_image(self, image_path: str) -> torch.Tensor:
        """
        Load and preprocess image for inference.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Preprocessed tensor [1, 3, 224, 224]
        """
        # Load image
        image = Image.open(image_path).convert('RGB')
        image_np = np.array(image)
        
        # Apply transforms
        transformed = self.transform(image=image_np)
        image_tensor = transformed['image']
        
        # Add batch dimension
        image_tensor = image_tensor.unsqueeze(0)
        
        return image_tensor
    
    def predict(
        self,
        image_path: str,
        return_all_probs: bool = True
    ) -> Dict:
        """
        Predict skin lesion class with uncertainty detection.
        
        Args:
            image_path: Path to image
            return_all_probs: Return probabilities for all classes
            
        Returns:
            Dictionary with prediction results:
            {
                'prediction': class name or None (if uncertain),
                'confidence': max probability,
                'uncertain': bool,
                'message': explanation,
                'all_probabilities': dict of all class probabilities (optional)
            }
        """
        # Preprocess
        image_tensor = self.preprocess_image(image_path).to(self.device)
        
        # Inference with temperature scaling
        with torch.no_grad():
            logits = self.model.forward_with_temperature(image_tensor)
            probabilities = torch.softmax(logits, dim=1)
        
        # Get top prediction
        max_prob, pred_idx = torch.max(probabilities, dim=1)
        max_prob = max_prob.item()
        pred_idx = pred_idx.item()
        
        # Class name
        class_code = self.idx_to_class[pred_idx]
        class_name = self.class_names[class_code]
        
        # Uncertainty detection
        is_uncertain = max_prob < self.confidence_threshold
        
        # Build result
        result = {
            'prediction': None if is_uncertain else class_name,
            'predicted_class_code': class_code,
            'confidence': max_prob,
            'uncertain': is_uncertain,
        }
        
        # Add message
        if is_uncertain:
            result['message'] = (
                f"⚠️ Model confidence below {self.confidence_threshold:.0%} threshold. "
                f"Recommend dermatologist review. "
                f"Top prediction was {class_name} with {max_prob:.1%} confidence."
            )
        else:
            result['message'] = f"Prediction: {class_name} ({max_prob:.1%} confidence)"
        
        # Add all probabilities if requested
        if return_all_probs:
            all_probs = {}
            probs_np = probabilities.cpu().numpy()[0]
            
            for idx, prob in enumerate(probs_np):
                code = self.idx_to_class[idx]
                name = self.class_names[code]
                all_probs[name] = float(prob)
            
            # Sort by probability
            result['all_probabilities'] = dict(
                sorted(all_probs.items(), key=lambda x: x[1], reverse=True)
            )
        
        return result
    
    def predict_batch(self, image_paths: list) -> list:
        """
        Predict on multiple images.
        
        Args:
            image_paths: List of image paths
            
        Returns:
            List of prediction dictionaries
        """
        results = []
        for image_path in image_paths:
            result = self.predict(image_path)
            result['image_path'] = image_path
            results.append(result)
        
        return results

    def predict_with_gradcam(
        self,
        image_path: str,
        return_all_probs: bool = True
    ) -> Dict:
        """
        Predict with Grad-CAM visualization.
        
        Args:
            image_path: Path to image
            return_all_probs: Return all probabilities
            
        Returns:
            Prediction dict + gradcam_overlay (numpy array)
        """
        from ml.src.visualization.gradcam import create_gradcam_visualization
        
        # Get prediction
        result = self.predict(image_path, return_all_probs)
        
        # Generate Grad-CAM
        original, overlayed = create_gradcam_visualization(
            model=self.model,
            image_path=image_path,
            device=self.device,
            target_class=None  # Use predicted class
        )
        
        result['original_image'] = original
        result['gradcam_overlay'] = overlayed
        
        return result