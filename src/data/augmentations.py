"""
DermaVision — Albumentations Augmentation Pipelines.

Provides train-time and validation/test-time transforms tailored for
dermatoscopic image classification.

Train augmentations (per design spec):
  - RandomRotate90
  - HorizontalFlip, VerticalFlip
  - RandomBrightnessContrast
  - HueSaturationValue
  - CoarseDropout (simulate occlusions)
  - Normalize (ImageNet stats)
"""

import albumentations as A
from albumentations.pytorch import ToTensorV2


def get_train_transforms(image_size: int = 224) -> A.Compose:
    """Training augmentation pipeline.

    Matches the design specification augmentations exactly:
    geometric flips/rotations, color jitter, and occlusion simulation.

    Args:
        image_size: Target image size (default: 224 per spec).

    Returns:
        Albumentations Compose pipeline.
    """
    return A.Compose([
        A.Resize(image_size, image_size),

        # Geometric transforms
        A.RandomRotate90(p=0.5),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),

        # Color transforms
        A.RandomBrightnessContrast(
            brightness_limit=0.2,
            contrast_limit=0.2,
            p=0.5,
        ),
        A.HueSaturationValue(
            hue_shift_limit=20,
            sat_shift_limit=30,
            val_shift_limit=20,
            p=0.5,
        ),

        # Simulate occlusions
        A.CoarseDropout(
            max_holes=8,
            max_height=image_size // 10,
            max_width=image_size // 10,
            fill_value=0,
            p=0.3,
        ),

        # Normalize with ImageNet stats and convert to tensor
        A.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
        ToTensorV2(),
    ])


def get_val_transforms(image_size: int = 224) -> A.Compose:
    """Validation/Test augmentation pipeline (deterministic).

    Only resizes and normalizes — no random augmentations.

    Args:
        image_size: Target image size (default: 224 per spec).

    Returns:
        Albumentations Compose pipeline.
    """
    return A.Compose([
        A.Resize(image_size, image_size),
        A.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
        ToTensorV2(),
    ])
