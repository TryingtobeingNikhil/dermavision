"""
DermaVision — PyTorch Dataset for HAM10000 Skin Lesion Classification.

Handles image loading, label encoding, and augmentation pipeline integration.
"""

import os

import numpy as np
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset


class DermaDataset(Dataset):
    """Custom PyTorch Dataset for HAM10000 dermatoscopic images.

    Args:
        metadata_df (pd.DataFrame): DataFrame with columns ['image_id', 'dx', 'split'].
        image_dir (str): Path to directory containing images.
        transform (callable, optional): Albumentations transform pipeline.
        class_to_idx (dict, optional): Mapping from class abbreviation to index.

    Example:
        >>> dataset = DermaDataset(
        ...     metadata_df=train_df,
        ...     image_dir="data/processed",
        ...     transform=get_train_transforms()
        ... )
        >>> image, label = dataset[0]
    """

    DEFAULT_CLASS_MAP = {
        "akiec": 0, "bcc": 1, "bkl": 2, "df": 3,
        "mel": 4, "nv": 5, "vasc": 6,
    }

    def __init__(
        self,
        metadata_df: pd.DataFrame,
        image_dir: str,
        transform=None,
        class_to_idx: dict | None = None,
    ):
        self.metadata = metadata_df.reset_index(drop=True)
        self.image_dir = image_dir
        self.transform = transform
        self.class_to_idx = class_to_idx or self.DEFAULT_CLASS_MAP

        # Pre-compute labels
        self.labels = self.metadata["dx"].map(self.class_to_idx).values
        self.image_ids = self.metadata["image_id"].values

    def __len__(self) -> int:
        return len(self.metadata)

    def __getitem__(self, idx: int) -> tuple:
        """Return (image_tensor, label) for a given index."""
        image_id = self.image_ids[idx]
        label = self.labels[idx]

        # Load image
        img_path = os.path.join(self.image_dir, f"{image_id}.jpg")
        image = np.array(Image.open(img_path).convert("RGB"))

        # Apply augmentations
        if self.transform:
            augmented = self.transform(image=image)
            image = augmented["image"]

        return image, label

    def get_class_weights(self) -> np.ndarray:
        """Compute inverse-frequency class weights for imbalanced data."""
        class_counts = np.bincount(self.labels, minlength=len(self.class_to_idx))
        total = len(self.labels)
        weights = total / (len(self.class_to_idx) * class_counts + 1e-6)
        return weights / weights.sum() * len(self.class_to_idx)

    def get_class_distribution(self) -> dict:
        """Return class distribution as {class_name: count}."""
        idx_to_class = {v: k for k, v in self.class_to_idx.items()}
        counts = np.bincount(self.labels, minlength=len(self.class_to_idx))
        return {idx_to_class[i]: int(c) for i, c in enumerate(counts)}
