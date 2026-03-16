"""
EfficientNet-B3 Model for Skin Lesion Classification

Architecture:
- Pretrained EfficientNet-B3 backbone
- Custom classification head
- Dropout for regularization
- Temperature scaling for calibrated uncertainty
"""

import torch
import torch.nn as nn
from torchvision import models
from typing import Optional


class SkinLesionClassifier(nn.Module):
    """
    EfficientNet-B3 based skin lesion classifier.
    
    Features:
    - Transfer learning from ImageNet
    - Custom head for 7-class classification
    - Dropout regularization
    - Temperature scaling for uncertainty calibration
    
    Args:
        num_classes: Number of disease classes (default 7)
        pretrained: Use ImageNet pretrained weights
        dropout: Dropout probability (default 0.3)
        freeze_backbone: Freeze EfficientNet layers initially
    """
    
    def __init__(
        self,
        num_classes: int = 7,
        pretrained: bool = True,
        dropout: float = 0.3,
        freeze_backbone: bool = False
    ):
        super().__init__()
        
        self.num_classes = num_classes
        
        # Load pretrained EfficientNet-B3
        weights = models.EfficientNet_B3_Weights.IMAGENET1K_V1 if pretrained else None
        self.backbone = models.efficientnet_b3(weights=weights)
        
        # Get the number of features from the backbone
        # EfficientNet-B3 outputs 1536 features
        num_features = self.backbone.classifier[1].in_features
        
        # Replace the classifier head
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=dropout, inplace=True),
            nn.Linear(num_features, num_classes)
        )
        
        # Temperature parameter for calibration (learnable)
        # Initialized to 1.0 (no scaling initially)
        self.temperature = nn.Parameter(torch.ones(1) * 1.5)
        
        # Optionally freeze backbone for initial training
        if freeze_backbone:
            self._freeze_backbone()
        
        print(f"✅ Model initialized:")
        print(f"   Backbone: EfficientNet-B3 ({'pretrained' if pretrained else 'random init'})")
        print(f"   Classifier: {num_features} → {num_classes}")
        print(f"   Dropout: {dropout}")
        print(f"   Backbone frozen: {freeze_backbone}")
    
    def _freeze_backbone(self):
        """Freeze all backbone parameters."""
        for param in self.backbone.features.parameters():
            param.requires_grad = False
        print("   🔒 Backbone frozen (only classifier will train)")
    
    def unfreeze_backbone(self):
        """Unfreeze backbone for fine-tuning."""
        for param in self.backbone.features.parameters():
            param.requires_grad = True
        print("   🔓 Backbone unfrozen (full model fine-tuning)")
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor [batch_size, 3, 224, 224]
            
        Returns:
            Logits tensor [batch_size, num_classes]
        """
        logits = self.backbone(x)
        return logits
    
    def forward_with_temperature(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass with temperature scaling for calibrated probabilities.
        
        Used during inference for uncertainty estimation.
        
        Args:
            x: Input tensor [batch_size, 3, 224, 224]
            
        Returns:
            Temperature-scaled logits [batch_size, num_classes]
        """
        logits = self.backbone(x)
        # Scale logits by temperature (lower temp = more confident)
        return logits / self.temperature
    
    def get_num_params(self) -> dict:
        """
        Count model parameters.
        
        Returns:
            Dictionary with total, trainable, and frozen parameter counts
        """
        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        frozen = total - trainable
        
        return {
            'total': total,
            'trainable': trainable,
            'frozen': frozen
        }


def create_model(
    num_classes: int = 7,
    pretrained: bool = True,
    dropout: float = 0.3,
    freeze_backbone: bool = False,
    device: Optional[str] = None
) -> SkinLesionClassifier:
    """
    Factory function to create and initialize model.
    
    Args:
        num_classes: Number of output classes
        pretrained: Use ImageNet weights
        dropout: Dropout probability
        freeze_backbone: Freeze backbone initially
        device: Device to move model to ('mps', 'cuda', 'cpu')
        
    Returns:
        Initialized model
    """
    model = SkinLesionClassifier(
        num_classes=num_classes,
        pretrained=pretrained,
        dropout=dropout,
        freeze_backbone=freeze_backbone
    )
    
    # Auto-detect device if not specified
    if device is None:
        if torch.backends.mps.is_available():
            device = 'mps'
        elif torch.cuda.is_available():
            device = 'cuda'
        else:
            device = 'cpu'
    
    model = model.to(device)
    
    # Print parameter counts
    param_counts = model.get_num_params()
    print(f"\n📊 Model Parameters:")
    print(f"   Total:     {param_counts['total']:,}")
    print(f"   Trainable: {param_counts['trainable']:,}")
    print(f"   Frozen:    {param_counts['frozen']:,}")
    print(f"   Device:    {device}")
    
    return model