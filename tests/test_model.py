"""
DermaVision — Model Tests.

Tests for model architecture, forward pass, and loss function.
"""

import numpy as np
import pytest
import torch


class TestDermaModel:
    """Tests for the DermaModel architecture."""

    def test_model_output_shape(self):
        """Verify model output shape matches num_classes."""
        from src.models.cnn_model import DermaModel

        model = DermaModel(num_classes=7, pretrained=False)
        x = torch.randn(2, 3, 300, 300)
        output = model(x)

        assert output.shape == (2, 7)

    def test_model_feature_extraction(self):
        """Verify feature extraction produces embeddings."""
        from src.models.cnn_model import DermaModel

        model = DermaModel(num_classes=7, pretrained=False)
        x = torch.randn(1, 3, 300, 300)
        features = model.get_features(x)

        assert features.dim() == 2
        assert features.shape[0] == 1

    def test_backbone_freezing(self):
        """Verify backbone freezing works correctly."""
        from src.models.cnn_model import DermaModel

        model = DermaModel(num_classes=7, pretrained=False)
        model.freeze_backbone(True)

        for param in model.backbone.parameters():
            assert not param.requires_grad

        model.freeze_backbone(False)

        for param in model.backbone.parameters():
            assert param.requires_grad


class TestFocalLoss:
    """Tests for the Focal Loss implementation."""

    def test_focal_loss_output_scalar(self):
        """Verify focal loss returns a scalar."""
        from src.models.loss import FocalLoss

        criterion = FocalLoss(gamma=2.0)
        inputs = torch.randn(4, 7)
        targets = torch.tensor([0, 1, 2, 3])

        loss = criterion(inputs, targets)
        assert loss.dim() == 0  # Scalar

    def test_focal_loss_with_alpha(self):
        """Verify focal loss works with class weights."""
        from src.models.loss import FocalLoss

        alpha = torch.ones(7) / 7
        criterion = FocalLoss(gamma=2.0, alpha=alpha)
        inputs = torch.randn(8, 7)
        targets = torch.randint(0, 7, (8,))

        loss = criterion(inputs, targets)
        assert loss.item() > 0

    def test_focal_loss_gamma_zero_equals_ce(self):
        """Verify gamma=0 approximates standard cross-entropy."""
        from src.models.loss import FocalLoss

        torch.manual_seed(42)
        inputs = torch.randn(16, 7)
        targets = torch.randint(0, 7, (16,))

        focal = FocalLoss(gamma=0.0)(inputs, targets)
        ce = torch.nn.functional.cross_entropy(inputs, targets)

        assert abs(focal.item() - ce.item()) < 1e-5
