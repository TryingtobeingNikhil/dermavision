"""
DermaVision — Grad-CAM Implementation.

Gradient-weighted Class Activation Mapping for visual explanations
of CNN predictions on dermatoscopic images.
"""

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image


class GradCAM:
    """Grad-CAM: Visual Explanations from Deep Networks.

    Generates heatmaps showing which regions of the input image
    most influenced the model's prediction.

    Args:
        model: Trained PyTorch model.
        target_layer: Name of the target convolutional layer.
        device: Compute device.

    Reference:
        Selvaraju et al., "Grad-CAM: Visual Explanations from Deep Networks
        via Gradient-based Localization", ICCV 2017.

    Example:
        >>> gradcam = GradCAM(model, target_layer="backbone.conv_head")
        >>> heatmap, overlay = gradcam.generate("image.jpg")
    """

    def __init__(
        self,
        model: torch.nn.Module,
        target_layer: str = "backbone.conv_head",
        device: str = "cpu",
    ):
        self.model = model.eval()
        self.device = device

        # Register hooks
        self.gradients = None
        self.activations = None

        target = self._get_layer(target_layer)
        target.register_forward_hook(self._forward_hook)
        target.register_full_backward_hook(self._backward_hook)

    def _get_layer(self, layer_name: str) -> torch.nn.Module:
        """Get a layer by dot-separated name."""
        module = self.model
        for name in layer_name.split("."):
            module = getattr(module, name)
        return module

    def _forward_hook(self, module, input, output):
        self.activations = output.detach()

    def _backward_hook(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate(
        self,
        image: np.ndarray,
        transform=None,
        target_class: int | None = None,
        colormap: int = cv2.COLORMAP_JET,
        alpha: float = 0.4,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Generate Grad-CAM heatmap for an image.

        Args:
            image: Input image as numpy array (H, W, 3) in RGB.
            transform: Preprocessing transform (uses val transforms if None).
            target_class: Target class index. If None, uses predicted class.
            colormap: OpenCV colormap for heatmap visualization.
            alpha: Blend factor for overlay (0-1).

        Returns:
            Tuple of (heatmap, overlay):
                - heatmap: Normalized heatmap array (H, W) in [0, 1].
                - overlay: Blended image with heatmap overlay (H, W, 3).
        """
        self.model.eval()

        # Preprocess
        if transform:
            processed = transform(image=image)
            input_tensor = processed["image"].unsqueeze(0).to(self.device)
        else:
            from ..data.augmentations import get_val_transforms
            transform = get_val_transforms()
            processed = transform(image=image)
            input_tensor = processed["image"].unsqueeze(0).to(self.device)

        # Forward pass
        input_tensor.requires_grad_(True)
        output = self.model(input_tensor)

        if target_class is None:
            target_class = output.argmax(dim=1).item()

        # Backward pass
        self.model.zero_grad()
        target_score = output[0, target_class]
        target_score.backward()

        # Compute Grad-CAM
        gradients = self.gradients
        activations = self.activations

        # Global average pooling of gradients
        weights = torch.mean(gradients, dim=[2, 3], keepdim=True)

        # Weighted combination of activation maps
        cam = torch.sum(weights * activations, dim=1, keepdim=True)
        cam = F.relu(cam)  # Only positive contributions

        # Normalize
        cam = cam.squeeze().cpu().numpy()
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)

        # Resize to original image size
        h, w = image.shape[:2]
        heatmap = cv2.resize(cam, (w, h))

        # Create overlay
        heatmap_colored = cv2.applyColorMap(
            np.uint8(255 * heatmap), colormap
        )
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

        overlay = np.float32(heatmap_colored) * alpha + np.float32(image) * (1 - alpha)
        overlay = np.uint8(np.clip(overlay, 0, 255))

        return heatmap, overlay
