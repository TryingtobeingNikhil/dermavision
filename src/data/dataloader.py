"""
DermaVision — DataLoader Setup.

Creates train, validation, and test DataLoaders with proper sampling
strategy for imbalanced classes.
"""

import pandas as pd
import torch
from torch.utils.data import DataLoader, WeightedRandomSampler

from .augmentations import get_train_transforms, get_val_transforms
from .dataset import DermaDataset


def create_dataloaders(
    metadata_path: str,
    image_dir: str,
    batch_size: int = 32,
    image_size: int = 300,
    num_workers: int = 4,
    pin_memory: bool = True,
    use_weighted_sampling: bool = True,
) -> dict[str, DataLoader]:
    """Create train, validation, and test DataLoaders.

    Uses WeightedRandomSampler for the training set to handle class imbalance.

    Args:
        metadata_path: Path to metadata CSV with 'split' column.
        image_dir: Path to image directory.
        batch_size: Batch size for all loaders.
        image_size: Target image size.
        num_workers: Number of data loading workers.
        pin_memory: Whether to pin memory for GPU transfer.
        use_weighted_sampling: Use weighted sampling for training set.

    Returns:
        Dictionary with 'train', 'val', 'test' DataLoaders.
    """
    metadata = pd.read_csv(metadata_path, comment="#")

    splits = {}
    for split_name in ["train", "val", "test"]:
        split_df = metadata[metadata["split"] == split_name]
        transform = (
            get_train_transforms(image_size)
            if split_name == "train"
            else get_val_transforms(image_size)
        )
        splits[split_name] = DermaDataset(
            metadata_df=split_df,
            image_dir=image_dir,
            transform=transform,
        )

    # Weighted sampling for training set
    train_sampler = None
    shuffle_train = True

    if use_weighted_sampling and "train" in splits:
        train_dataset = splits["train"]
        class_weights = train_dataset.get_class_weights()
        sample_weights = [class_weights[label] for label in train_dataset.labels]
        train_sampler = WeightedRandomSampler(
            weights=sample_weights,
            num_samples=len(sample_weights),
            replacement=True,
        )
        shuffle_train = False  # Sampler handles shuffling

    dataloaders = {
        "train": DataLoader(
            splits["train"],
            batch_size=batch_size,
            shuffle=shuffle_train,
            sampler=train_sampler,
            num_workers=num_workers,
            pin_memory=pin_memory,
            drop_last=True,
        ),
        "val": DataLoader(
            splits["val"],
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
        ),
        "test": DataLoader(
            splits["test"],
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
        ),
    }

    return dataloaders
