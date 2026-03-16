"""
DermaVision — Confidence Calibration & Uncertainty Estimation.

Implements temperature scaling for post-hoc calibration of model
confidence, critical for medical decision support.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader


class TemperatureScaling(nn.Module):
    """Temperature scaling for post-hoc confidence calibration.

    Learns a single temperature parameter T that scales the logits
    before softmax to produce better-calibrated probabilities.

    Calibrated probability: softmax(logits / T)

    Args:
        initial_temperature: Starting temperature value.

    Reference:
        Guo et al., "On Calibration of Modern Neural Networks", ICML 2017.
    """

    def __init__(self, initial_temperature: float = 1.5):
        super().__init__()
        self.temperature = nn.Parameter(
            torch.tensor(initial_temperature, dtype=torch.float32)
        )

    def forward(self, logits: torch.Tensor) -> torch.Tensor:
        """Apply temperature scaling to logits.

        Args:
            logits: Raw model logits of shape (B, C).

        Returns:
            Temperature-scaled logits.
        """
        return logits / self.temperature

    def calibrate(
        self,
        model: nn.Module,
        val_loader: DataLoader,
        device: str = "cuda",
        lr: float = 0.01,
        max_iter: int = 100,
    ) -> float:
        """Learn optimal temperature from validation data.

        Uses NLL loss to find the temperature that best calibrates
        the model's confidence on the validation set.

        Args:
            model: Trained model (frozen).
            val_loader: Validation DataLoader.
            device: Compute device.
            lr: Learning rate for temperature optimization.
            max_iter: Maximum optimization iterations.

        Returns:
            Optimal temperature value.
        """
        model.eval()
        self.to(device)

        # Collect all logits and labels
        all_logits, all_labels = [], []

        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device)
                logits = model(images)
                all_logits.append(logits.cpu())
                all_labels.append(labels)

        all_logits = torch.cat(all_logits).to(device)
        all_labels = torch.cat(all_labels).to(device)

        # Optimize temperature
        optimizer = torch.optim.LBFGS([self.temperature], lr=lr, max_iter=max_iter)
        nll_criterion = nn.CrossEntropyLoss()

        def closure():
            optimizer.zero_grad()
            scaled_logits = self.forward(all_logits)
            loss = nll_criterion(scaled_logits, all_labels)
            loss.backward()
            return loss

        optimizer.step(closure)

        return self.temperature.item()


def calibrate_model(
    model: nn.Module,
    val_loader: DataLoader,
    device: str = "cuda",
) -> TemperatureScaling:
    """Convenience function to calibrate a trained model.

    Args:
        model: Trained model.
        val_loader: Validation DataLoader.
        device: Compute device.

    Returns:
        Fitted TemperatureScaling module.
    """
    temp_scaling = TemperatureScaling()
    optimal_temp = temp_scaling.calibrate(model, val_loader, device)
    print(f"  🌡  Optimal temperature: {optimal_temp:.4f}")
    return temp_scaling


def compute_ece(
    y_prob: np.ndarray,
    y_true: np.ndarray,
    n_bins: int = 15,
) -> float:
    """Compute Expected Calibration Error (ECE).

    Measures how well predicted probabilities align with actual accuracy
    across confidence bins.

    Args:
        y_prob: Predicted probabilities of shape (N, C).
        y_true: True labels of shape (N,).
        n_bins: Number of calibration bins.

    Returns:
        ECE value (lower is better).
    """
    confidences = np.max(y_prob, axis=1)
    predictions = np.argmax(y_prob, axis=1)
    accuracies = (predictions == y_true).astype(float)

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0

    for i in range(n_bins):
        mask = (confidences > bin_boundaries[i]) & (confidences <= bin_boundaries[i + 1])
        if mask.sum() > 0:
            bin_accuracy = accuracies[mask].mean()
            bin_confidence = confidences[mask].mean()
            bin_size = mask.sum() / len(y_true)
            ece += bin_size * abs(bin_accuracy - bin_confidence)

    return ece
