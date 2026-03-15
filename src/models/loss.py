"""
DermaVision — Focal Loss for Class Imbalance.

Implements Focal Loss (Lin et al., 2017) to down-weight easy examples
and focus training on hard, misclassified samples — critical for the
severely imbalanced HAM10000 dataset.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class FocalLoss(nn.Module):
    """Focal Loss for multi-class classification.

    Focal Loss = -alpha_t * (1 - p_t)^gamma * log(p_t)

    Down-weights well-classified examples, focusing the model on hard
    negatives. Particularly effective for datasets with extreme class
    imbalance like HAM10000 (nv:df ratio ~57:1).

    Args:
        gamma: Focusing parameter (default: 2.0). Higher values increase
               focus on hard examples.
        alpha: Per-class weights as tensor. If None, uniform weights are used.
        reduction: Loss reduction method ('mean', 'sum', 'none').

    Reference:
        Lin et al., "Focal Loss for Dense Object Detection", ICCV 2017.
    """

    def __init__(
        self,
        gamma: float = 2.0,
        alpha: torch.Tensor | None = None,
        reduction: str = "mean",
    ):
        super().__init__()
        self.gamma = gamma
        self.reduction = reduction

        if alpha is not None:
            self.register_buffer("alpha", alpha.float())
        else:
            self.alpha = None

    def forward(
        self, inputs: torch.Tensor, targets: torch.Tensor
    ) -> torch.Tensor:
        """Compute Focal Loss.

        Args:
            inputs: Predicted logits of shape (B, C).
            targets: Ground truth labels of shape (B,).

        Returns:
            Scalar loss value (if reduction != 'none').
        """
        ce_loss = F.cross_entropy(inputs, targets, reduction="none")
        p_t = torch.exp(-ce_loss)  # Probability of true class

        # Apply focal modulation
        focal_weight = (1 - p_t) ** self.gamma
        focal_loss = focal_weight * ce_loss

        # Apply class weights
        if self.alpha is not None:
            alpha_t = self.alpha[targets]
            focal_loss = alpha_t * focal_loss

        # Reduction
        if self.reduction == "mean":
            return focal_loss.mean()
        elif self.reduction == "sum":
            return focal_loss.sum()
        return focal_loss
