"""
Data Augmentation Pipeline for Dermoscopic Images

Design principles:
- Preserve medical features (avoid extreme transforms)
- Simulate real-world variations (lighting, rotation, hair)
- Different pipelines for train vs. val/test
"""

import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2


def get_train_transforms(image_size=224):
    """
    Training augmentations - balance realism with robustness.
    
    Args:
        image_size: Target image size (default 224 for EfficientNet)
        
    Returns:
        Albumentations Compose object
    """
    return A.Compose([
        # Geometric transforms (orientation-invariant)
        A.Resize(height=image_size, width=image_size, interpolation=cv2.INTER_LINEAR),
        A.RandomRotate90(p=0.5),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.Affine(
            translate_percent={"x": (-0.1, 0.1), "y": (-0.1, 0.1)},
            scale=(0.85, 1.15),
            rotate=(-45, 45),
            mode=cv2.BORDER_CONSTANT,
            p=0.5
        ),
        
        # Color/lighting transforms (mild to preserve skin tone info)
        A.RandomBrightnessContrast(
            brightness_limit=0.2,
            contrast_limit=0.2,
            p=0.5
        ),
        A.HueSaturationValue(
            hue_shift_limit=10,     # Very mild hue shift
            sat_shift_limit=20,
            val_shift_limit=15,
            p=0.4
        ),
        
        # Gaussian noise for robustness
        A.GaussNoise(std_range=(0.01, 0.05), p=0.3),
        
        # Simulate hair occlusions (common in dermoscopy)
        A.CoarseDropout(
            num_holes_range=(1, 8),
            hole_height_range=(4, 8),
            hole_width_range=(4, 8),
            fill=0,
            p=0.3
        ),
        
        # Normalization (ImageNet stats - for transfer learning)
        A.Normalize(
            mean=[0.485, 0.456, 0.406],  # ImageNet mean
            std=[0.229, 0.224, 0.225],   # ImageNet std
            max_pixel_value=255.0
        ),
        
        # Convert to PyTorch tensor
        ToTensorV2()
    ])


def get_valid_transforms(image_size=224):
    """
    Validation/Test transforms - minimal preprocessing only.
    
    Args:
        image_size: Target image size
        
    Returns:
        Albumentations Compose object
    """
    return A.Compose([
        A.Resize(height=image_size, width=image_size, interpolation=cv2.INTER_LINEAR),
        A.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
            max_pixel_value=255.0
        ),
        ToTensorV2()
    ])


def get_test_time_augmentation(image_size=224):
    """
    Test-Time Augmentation (TTA) - create multiple views of same image.
    
    Used during inference to improve predictions by averaging
    predictions across different augmented versions.
    
    Args:
        image_size: Target image size
        
    Returns:
        List of Albumentations Compose objects (one per TTA variant)
    """
    tta_transforms = [
        # Original
        A.Compose([
            A.Resize(image_size, image_size),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ]),
        # Horizontal flip
        A.Compose([
            A.Resize(image_size, image_size),
            A.HorizontalFlip(p=1.0),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ]),
        # Vertical flip
        A.Compose([
            A.Resize(image_size, image_size),
            A.VerticalFlip(p=1.0),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ]),
        # Rotate 90
        A.Compose([
            A.Resize(image_size, image_size),
            A.Rotate(limit=(90, 90), p=1.0),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ]),
    ]
    
    return tta_transforms