"""
Grad-CAM visualization for CNN interpretability.

Shows which regions of the image influenced the model's prediction.
"""

import torch
import torch.nn.functional as F
import cv2
import numpy as np
from PIL import Image
from typing import Tuple


class GradCAM:
    """
    Gradient-weighted Class Activation Mapping.
    
    Highlights which parts of the image the model focused on
    when making a prediction.
    """
    
    def __init__(self, model, target_layer):
        """
        Initialize Grad-CAM.
        
        Args:
            model: Trained CNN model
            target_layer: Layer to extract gradients from
                         (typically last conv layer)
        """
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Register hooks
        self._register_hooks()
    
    def _register_hooks(self):
        """Register forward and backward hooks."""
        
        def forward_hook(module, input, output):
            self.activations = output.detach()
        
        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()
        
        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)
    
    def generate_cam(
        self,
        input_image: torch.Tensor,
        target_class: int = None
    ) -> np.ndarray:
        """
        Generate Grad-CAM heatmap.
        
        Args:
            input_image: Preprocessed image tensor [1, 3, 224, 224]
            target_class: Class index to visualize (if None, uses predicted class)
            
        Returns:
            Heatmap array [224, 224]
        """
        # Forward pass
        self.model.eval()
        output = self.model(input_image)
        
        # Use predicted class if not specified
        if target_class is None:
            target_class = output.argmax(dim=1).item()
        
        # Zero gradients
        self.model.zero_grad()
        
        # Backward pass
        class_score = output[0, target_class]
        class_score.backward()
        
        # Get gradients and activations (same device as model/input)
        gradients = self.gradients[0]  # [C, H, W]
        activations = self.activations[0]  # [C, H, W]
        
        # Global average pooling on gradients
        weights = gradients.mean(dim=(1, 2))  # [C]
        
        # Weighted combination of activation maps on the same device
        cam = torch.zeros(
            activations.shape[1:],
            dtype=torch.float32,
            device=activations.device,
        )
        for i, w in enumerate(weights):
            cam += w * activations[i]
        
        # ReLU (only positive contributions)
        cam = F.relu(cam)
        
        # Normalize to [0, 1] and move to CPU for NumPy
        cam = cam.detach()
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        cam = cam.cpu().numpy()
        
        return cam
    
    def overlay_heatmap(
        self,
        original_image: np.ndarray,
        heatmap: np.ndarray,
        alpha: float = 0.4,
        colormap: int = cv2.COLORMAP_JET
    ) -> np.ndarray:
        """
        Overlay heatmap on original image.
        
        Args:
            original_image: Original image [H, W, 3] (RGB)
            heatmap: Grad-CAM heatmap [224, 224]
            alpha: Transparency of heatmap overlay
            colormap: OpenCV colormap
            
        Returns:
            Overlayed image [H, W, 3]
        """
        # Resize heatmap to match image size
        h, w = original_image.shape[:2]
        heatmap_resized = cv2.resize(heatmap, (w, h))
        
        # Convert to RGB colormap
        heatmap_colored = cv2.applyColorMap(
            np.uint8(255 * heatmap_resized),
            colormap
        )
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
        
        # Overlay
        overlayed = (1 - alpha) * original_image + alpha * heatmap_colored
        overlayed = np.uint8(overlayed)
        
        return overlayed


def create_gradcam_visualization(
    model,
    image_path: str,
    device: str = 'cpu',
    target_class: int = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create Grad-CAM visualization for an image.
    
    Args:
        model: Trained model
        image_path: Path to image
        device: Device to run on
        target_class: Class to visualize (None = predicted class)
        
    Returns:
        (original_image, overlayed_image) as numpy arrays
    """
    from ml.src.data.augmentations import get_valid_transforms
    
    # Load and preprocess image
    original_image = np.array(Image.open(image_path).convert('RGB'))
    
    transform = get_valid_transforms(image_size=224)
    transformed = transform(image=original_image)
    input_tensor = transformed['image'].unsqueeze(0).to(device)
    
    # Get target layer (last conv layer in EfficientNet backbone)
    target_layer = model.backbone.features[-1]
    
    # Create Grad-CAM and generate heatmap
    gradcam = GradCAM(model, target_layer)
    heatmap = gradcam.generate_cam(input_tensor, target_class=target_class)
    
    # Overlay heatmap on original image
    overlayed_image = gradcam.overlay_heatmap(original_image, heatmap)
    
    return original_image, overlayed_image