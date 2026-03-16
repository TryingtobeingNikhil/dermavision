"""Test loss functions and metrics."""

from pathlib import Path
import sys

import torch

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from ml.src.models.loss import FocalLoss, create_loss_function
from ml.src.models.metrics import MetricsCalculator
from ml.src.data.dataset import HAM10000Dataset


def test_focal_loss():
    """Test Focal Loss computation."""
    print("🧪 Testing Focal Loss\n")
    
    # Create dummy class weights
    class_weights = torch.tensor([3.0, 2.5, 1.5, 50.0, 1.3, 0.2, 8.0])
    
    # Create loss
    criterion = FocalLoss(alpha=class_weights, gamma=2.0)
    
    # Dummy batch
    batch_size = 16
    num_classes = 7
    
    logits = torch.randn(batch_size, num_classes)
    targets = torch.randint(0, num_classes, (batch_size,))
    
    # Compute loss
    loss = criterion(logits, targets)
    
    print(f"   Logits shape: {logits.shape}")
    print(f"   Targets shape: {targets.shape}")
    print(f"   Loss value: {loss.item():.4f}")
    print(f"   ✅ Focal Loss working!\n")


def test_metrics():
    """Test metrics calculation."""
    print("🧪 Testing Metrics Calculator\n")
    
    # Class names
    class_names = HAM10000Dataset.FULL_NAMES
    idx_to_class = HAM10000Dataset.IDX_TO_CLASS
    class_names_dict = {i: class_names[idx_to_class[i]] for i in range(7)}
    
    # Create metrics calculator
    metrics_calc = MetricsCalculator(num_classes=7, class_names=class_names_dict)
    
    # Simulate predictions
    num_samples = 100
    predictions = torch.randint(0, 7, (num_samples,))
    targets = torch.randint(0, 7, (num_samples,))
    probabilities = torch.softmax(torch.randn(num_samples, 7), dim=1)
    
    # Update metrics
    metrics_calc.update(predictions, targets, probabilities)
    
    # Compute and print
    metrics_calc.print_summary()
    
    print("\n✅ Metrics calculator working!")


if __name__ == "__main__":
    test_focal_loss()
    print()
    test_metrics()