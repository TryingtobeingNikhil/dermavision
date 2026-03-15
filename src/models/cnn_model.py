"""
DermaVision — CNN Model Architecture.

EfficientNet-B3 backbone with custom classification head for
7-class skin lesion classification.
"""

import torch
import torch.nn as nn
import timm


class DermaModel(nn.Module):
    """EfficientNet-B3 based classifier for skin lesion classification.

    Uses a pretrained EfficientNet-B3 backbone with a custom classification
    head featuring dropout for regularization.

    Args:
        num_classes: Number of output classes (default: 7 for HAM10000).
        pretrained: Whether to use ImageNet pretrained weights.
        dropout_rate: Dropout probability in the classification head.

    Example:
        >>> model = DermaModel(num_classes=7, pretrained=True)
        >>> x = torch.randn(1, 3, 300, 300)
        >>> logits = model(x)
        >>> logits.shape
        torch.Size([1, 7])
    """

    def __init__(
        self,
        num_classes: int = 7,
        pretrained: bool = True,
        dropout_rate: float = 0.3,
    ):
        super().__init__()

        # Load EfficientNet-B3 backbone
        self.backbone = timm.create_model(
            "efficientnet_b3",
            pretrained=pretrained,
            num_classes=0,  # Remove original head
        )

        # Get feature dimension from backbone
        in_features = self.backbone.num_features

        # Custom classification head
        self.classifier = nn.Sequential(
            nn.BatchNorm1d(in_features),
            nn.Dropout(dropout_rate),
            nn.Linear(in_features, 512),
            nn.ReLU(inplace=True),
            nn.BatchNorm1d(512),
            nn.Dropout(dropout_rate / 2),
            nn.Linear(512, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Args:
            x: Input tensor of shape (B, 3, H, W).

        Returns:
            Logits of shape (B, num_classes).
        """
        features = self.backbone(x)
        logits = self.classifier(features)
        return logits

    def get_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract feature embeddings (before classification head).

        Args:
            x: Input tensor of shape (B, 3, H, W).

        Returns:
            Feature tensor of shape (B, in_features).
        """
        return self.backbone(x)

    def freeze_backbone(self, freeze: bool = True) -> None:
        """Freeze/unfreeze backbone parameters for transfer learning.

        Args:
            freeze: If True, freeze backbone; if False, unfreeze.
        """
        for param in self.backbone.parameters():
            param.requires_grad = not freeze


def create_model(
    num_classes: int = 7,
    pretrained: bool = True,
    dropout_rate: float = 0.3,
    device: str = "auto",
) -> DermaModel:
    """Factory function to create and configure the model.

    Args:
        num_classes: Number of output classes.
        pretrained: Use ImageNet pretrained weights.
        dropout_rate: Dropout probability.
        device: Target device ('auto', 'cuda', 'cpu', 'mps').

    Returns:
        Configured DermaModel on the specified device.
    """
    if device == "auto":
        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"

    model = DermaModel(
        num_classes=num_classes,
        pretrained=pretrained,
        dropout_rate=dropout_rate,
    )

    return model.to(device)
