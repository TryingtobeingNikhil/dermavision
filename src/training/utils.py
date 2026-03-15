"""
DermaVision — Training Utilities.

Helper functions for reproducibility, configuration loading,
and device management.
"""

import json
import os
import random

import numpy as np
import torch
import yaml


def seed_everything(seed: int = 42) -> None:
    """Set random seeds for full reproducibility.

    Args:
        seed: Random seed value.
    """
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load YAML configuration file.

    Args:
        config_path: Path to the YAML config file.

    Returns:
        Configuration dictionary.
    """
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


def load_class_mapping(mapping_path: str = "config/class_mapping.json") -> dict:
    """Load class mapping from JSON file.

    Args:
        mapping_path: Path to class_mapping.json.

    Returns:
        Class mapping dictionary.
    """
    with open(mapping_path, "r") as f:
        mapping = json.load(f)
    return mapping


def get_device(preferred: str = "auto") -> torch.device:
    """Get the best available compute device.

    Args:
        preferred: Preferred device ('auto', 'cuda', 'mps', 'cpu').

    Returns:
        torch.device instance.
    """
    if preferred == "auto":
        if torch.cuda.is_available():
            device = torch.device("cuda")
            print(f"  🖥  Using CUDA: {torch.cuda.get_device_name(0)}")
        elif torch.backends.mps.is_available():
            device = torch.device("mps")
            print("  🍎 Using Apple MPS")
        else:
            device = torch.device("cpu")
            print("  💻 Using CPU")
    else:
        device = torch.device(preferred)

    return device


def count_parameters(model: torch.nn.Module) -> dict:
    """Count model parameters.

    Args:
        model: PyTorch model.

    Returns:
        Dictionary with total, trainable, and frozen parameter counts.
    """
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    frozen = total - trainable

    return {
        "total": total,
        "trainable": trainable,
        "frozen": frozen,
        "total_mb": total * 4 / (1024 ** 2),  # Approximate size in MB (float32)
    }
