"""
Training utilities.
"""

import torch
import random
import numpy as np


def set_seed(seed: int = 42):
    """
    Set random seed for reproducibility.
    
    Args:
        seed: Random seed value
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    
    # Make cudnn deterministic (slower but reproducible)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    
    print(f"Random seed set to {seed}")


def count_parameters(model):
    """Count trainable parameters."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def load_checkpoint(model, checkpoint_path, device='cpu'):
    """
    Load model from checkpoint.
    
    Args:
        model: Model instance
        checkpoint_path: Path to checkpoint file
        device: Device to load to
        
    Returns:
        model, epoch, metrics
    """
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    
    epoch = checkpoint.get('epoch', 0)
    metrics = {
        'best_val_loss': checkpoint.get('best_val_loss', float('inf')),
        'best_val_f1': checkpoint.get('best_val_f1', 0.0)
    }
    
    print(f"✅ Loaded checkpoint from epoch {epoch}")
    print(f"   Best val F1: {metrics['best_val_f1']:.4f}")
    
    return model, epoch, metrics