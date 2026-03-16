"""
Loss Functions for Imbalanced Medical Image Classification

Implements:
- Focal Loss: Focuses on hard examples and rare classes
- Weighted CrossEntropy: Alternative baseline
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class FocalLoss(nn.Module):
    """
    Focal Loss for addressing class imbalance.
    
    Paper: "Focal Loss for Dense Object Detection" (Lin et al., 2017)
    Formula: FL(p_t) = -α_t * (1 - p_t)^γ * log(p_t)
    
    Where:
    - p_t: model's estimated probability for the true class
    - α_t: class weight (higher for rare classes)
    - γ (gamma): focusing parameter (typically 2.0)
        - γ = 0: equivalent to CrossEntropy
        - γ > 0: down-weights easy examples, focuses on hard ones
    
    Args:
        alpha: Class weights tensor [num_classes]
        gamma: Focusing parameter (default 2.0)
        reduction: 'mean' or 'sum'
        
    Example:
        >>> from ml.src.data.dataset import HAM10000Dataset
        >>> train_dataset = HAM10000Dataset(...)
        >>> class_weights = train_dataset.get_class_weights()
        >>> criterion = FocalLoss(alpha=class_weights, gamma=2.0)
    """
    
    def __init__(
        self,
        alpha: torch.Tensor = None,
        gamma: float = 2.0,
        label_smoothing: float = 0.0,
        reduction: str = 'mean'
    ):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.label_smoothing = label_smoothing
        self.reduction = reduction
        
        print(f"✅ Focal Loss initialized:")
        print(f"   Gamma: {gamma}")
        print(f"   Alpha (class weights): {'Enabled' if alpha is not None else 'Disabled'}")
        print(f"   Label smoothing: {label_smoothing}")
        print(f"   Reduction: {reduction}")
    
    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Compute focal loss.
        
        Args:
            inputs: Model logits [batch_size, num_classes]
            targets: Ground truth labels [batch_size]
            
        Returns:
            Loss scalar
        """
        # Compute cross entropy (with optional label smoothing)
        ce_loss = F.cross_entropy(
            inputs, targets, reduction='none',
            label_smoothing=self.label_smoothing
        )
        
        # Get probabilities
        probs = torch.softmax(inputs, dim=1)
        
        # Get probability of true class for each sample
        p_t = probs.gather(1, targets.unsqueeze(1)).squeeze(1)
        
        # Compute focal term: (1 - p_t)^gamma
        focal_term = (1 - p_t) ** self.gamma
        
        # Compute focal loss
        loss = focal_term * ce_loss
        
        # Apply class weights if provided
        if self.alpha is not None:
            # Ensure alpha is on same device as loss
            if self.alpha.device != loss.device:
                self.alpha = self.alpha.to(loss.device)
            
            # Get weight for each sample based on its class
            alpha_t = self.alpha.gather(0, targets)
            loss = alpha_t * loss
        
        # Apply reduction
        if self.reduction == 'mean':
            return loss.mean()
        elif self.reduction == 'sum':
            return loss.sum()
        else:
            return loss


class WeightedCrossEntropyLoss(nn.Module):
    """
    Weighted Cross-Entropy Loss (baseline alternative to Focal Loss).
    
    Simple class-weighted version of standard CrossEntropy.
    Useful for ablation studies.
    
    Args:
        weight: Class weights tensor [num_classes]
    """
    
    def __init__(self, weight: torch.Tensor = None):
        super().__init__()
        self.weight = weight
        print(f"✅ Weighted CrossEntropy initialized")
    
    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Compute weighted cross-entropy.
        
        Args:
            inputs: Model logits [batch_size, num_classes]
            targets: Ground truth labels [batch_size]
            
        Returns:
            Loss scalar
        """
        # Ensure weight is on same device
        weight = self.weight
        if weight is not None and weight.device != inputs.device:
            weight = weight.to(inputs.device)
        
        return F.cross_entropy(inputs, targets, weight=weight)


def create_loss_function(
    loss_type: str = 'focal',
    class_weights: torch.Tensor = None,
    gamma: float = 2.0,
    label_smoothing: float = 0.0
) -> nn.Module:
    """
    Factory function to create loss function.
    
    Args:
        loss_type: 'focal' or 'weighted_ce'
        class_weights: Class weights from dataset
        gamma: Focal loss gamma parameter
        label_smoothing: Label smoothing factor (0.0 = no smoothing)
        
    Returns:
        Loss function module
    """
    if loss_type == 'focal':
        return FocalLoss(alpha=class_weights, gamma=gamma, label_smoothing=label_smoothing)
    elif loss_type == 'weighted_ce':
        return WeightedCrossEntropyLoss(weight=class_weights)
    else:
        raise ValueError(f"Unknown loss type: {loss_type}")