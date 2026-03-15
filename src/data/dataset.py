"""
HAM10000 PyTorch Dataset

Handles:
- Loading images from split folders
- Label encoding
- Train/val/test splits
- Augmentation pipeline integration
"""

import torch
from torch.utils.data import Dataset
from pathlib import Path
from PIL import Image
import pandas as pd
import numpy as np


class HAM10000Dataset(Dataset):
    """
    PyTorch Dataset for HAM10000 skin lesion images.
    
    Args:
        metadata_path: Path to metadata.csv
        data_dir: Path to processed data directory
        split: 'train', 'val', or 'test'
        transform: Albumentations transform pipeline
        
    Example:
        >>> from src.data.augmentations import get_train_transforms
        >>> train_dataset = HAM10000Dataset(
        ...     metadata_path='data/metadata.csv',
        ...     data_dir='data/processed',
        ...     split='train',
        ...     transform=get_train_transforms()
        ... )
    """
    
    # Class mapping (consistent ordering for model output)
    CLASS_NAMES = {
        'akiec': 0,  # Actinic keratoses
        'bcc': 1,    # Basal cell carcinoma
        'bkl': 2,    # Benign keratosis
        'df': 3,     # Dermatofibroma
        'mel': 4,    # Melanoma (our critical class!)
        'nv': 5,     # Melanocytic nevi
        'vasc': 6    # Vascular lesions
    }
    
    # Reverse mapping for predictions
    IDX_TO_CLASS = {v: k for k, v in CLASS_NAMES.items()}
    
    # Full disease names for display
    FULL_NAMES = {
        'akiec': 'Actinic Keratoses',
        'bcc': 'Basal Cell Carcinoma',
        'bkl': 'Benign Keratosis',
        'df': 'Dermatofibroma',
        'mel': 'Melanoma',
        'nv': 'Melanocytic Nevi',
        'vasc': 'Vascular Lesions'
    }
    
    def __init__(
        self,
        metadata_path: str,
        data_dir: str,
        split: str = 'train',
        transform=None
    ):
        """Initialize dataset."""
        self.data_dir = Path(data_dir)
        self.split = split
        self.transform = transform
        
        # Load metadata and filter by split
        self.metadata = pd.read_csv(metadata_path)
        self.data = self.metadata[self.metadata['split'] == split].reset_index(drop=True)
        
        # Image folders (check both part_1 and part_2)
        self.image_folders = [
            self.data_dir / 'HAM10000_images_part_1',
            self.data_dir / 'HAM10000_images_part_2'
        ]
        
        print(f"✅ Loaded {len(self.data)} {split} samples")
        
        # Print class distribution for this split
        self._print_class_distribution()
    
    def _print_class_distribution(self):
        """Print class distribution for this split."""
        class_counts = self.data['dx'].value_counts()
        print(f"\n📊 Class distribution ({self.split}):")
        for cls, count in class_counts.items():
            pct = (count / len(self.data) * 100)
            print(f"   {cls:6s} ({self.FULL_NAMES[cls]:25s}): {count:4d} ({pct:5.2f}%)")
    
    def _load_image(self, image_id: str) -> Image.Image:
        """
        Load image from either part_1 or part_2 folder.
        
        Args:
            image_id: Image ID (without .jpg extension)
            
        Returns:
            PIL Image
        """
        img_name = f"{image_id}.jpg"
        
        # Check both folders
        for folder in self.image_folders:
            img_path = folder / img_name
            if img_path.exists():
                return Image.open(img_path).convert('RGB')
        
        raise FileNotFoundError(f"Image {img_name} not found in any folder")
    
    def __len__(self) -> int:
        """Return dataset size."""
        return len(self.data)
    
    def __getitem__(self, idx: int) -> dict:
        """
        Get a single sample.
        
        Args:
            idx: Sample index
            
        Returns:
            Dictionary with 'image' (tensor) and 'label' (int)
        """
        # Get metadata for this sample
        row = self.data.iloc[idx]
        
        # Load image
        image = self._load_image(row['image_id'])
        
        # Convert to numpy for albumentations
        image_np = np.array(image)
        
        # Apply transforms
        if self.transform:
            transformed = self.transform(image=image_np)
            image_tensor = transformed['image']
        else:
            # If no transform, just convert to tensor
            image_tensor = torch.from_numpy(image_np).permute(2, 0, 1).float() / 255.0
        
        # Get label
        label = self.CLASS_NAMES[row['dx']]
        
        return {
            'image': image_tensor,
            'label': label,
            'image_id': row['image_id']  # Useful for debugging
        }
    
    def get_class_weights(self) -> torch.Tensor:
        """
        Calculate class weights for handling imbalance.
        
        Uses inverse frequency weighting:
        weight[i] = total_samples / (num_classes * class_count[i])
        
        Returns:
            Tensor of shape [num_classes] with weights
        """
        class_counts = self.data['dx'].value_counts()
        num_classes = len(self.CLASS_NAMES)
        total_samples = len(self.data)
        
        # Calculate weights
        weights = torch.zeros(num_classes)
        for cls, count in class_counts.items():
            cls_idx = self.CLASS_NAMES[cls]
            weights[cls_idx] = total_samples / (num_classes * count)
        
        print(f"\n⚖️  Class weights ({self.split}):")
        for cls, idx in self.CLASS_NAMES.items():
            print(f"   {cls:6s}: {weights[idx]:.3f}")
        
        return weights