"""
DataLoader Factory with Class Balancing

Handles:
- Weighted sampling for class imbalance
- Optimal batch sizes for M2 Air
- MPS-compatible data loading
- Pin memory for faster GPU transfer
"""

import torch
from torch.utils.data import DataLoader, WeightedRandomSampler
import numpy as np
from typing import Optional


def create_weighted_sampler(dataset):
    """
    Create a weighted sampler to balance class distribution.
    
    Strategy: Each sample's probability ∝ 1/class_frequency
    Result: Rare classes (df, vasc) appear more often in batches
    
    Args:
        dataset: HAM10000Dataset instance
        
    Returns:
        WeightedRandomSampler
    """
    # Get class counts
    class_counts = dataset.data['dx'].value_counts().to_dict()
    
    # Calculate sample weights (inverse frequency)
    sample_weights = []
    for idx in range(len(dataset)):
        label_name = dataset.data.iloc[idx]['dx']
        # Weight = 1 / class_frequency
        weight = 1.0 / class_counts[label_name]
        sample_weights.append(weight)
    
    # Create sampler
    sampler = WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(sample_weights),
        replacement=True  # Allow same sample multiple times per epoch
    )
    
    # Print sampling statistics
    print(f"\n🎲 Weighted Sampler Statistics:")
    print(f"   Total samples: {len(sample_weights)}")
    print(f"   Weight range: {min(sample_weights):.6f} - {max(sample_weights):.6f}")
    print(f"   → Rare classes will appear ~{max(sample_weights)/min(sample_weights):.1f}x more often")
    
    return sampler


def get_dataloader(
    dataset,
    batch_size: int = 32,
    shuffle: bool = True,
    use_weighted_sampling: bool = False,
    num_workers: int = 2,
    pin_memory: bool = True
) -> DataLoader:
    """
    Create a DataLoader with optimal settings for M2 Air.
    
    Args:
        dataset: HAM10000Dataset instance
        batch_size: Batch size (default 32 for M2 Air)
        shuffle: Whether to shuffle data (ignored if using weighted sampling)
        use_weighted_sampling: Use weighted sampler for class balancing
        num_workers: Number of data loading workers (2-4 optimal for M2)
        pin_memory: Pin memory for faster MPS transfer
        
    Returns:
        DataLoader
    """
    # Create sampler if requested
    sampler = None
    if use_weighted_sampling and dataset.split == 'train':
        sampler = create_weighted_sampler(dataset)
        shuffle = False  # Can't use both sampler and shuffle
        print(f"   ✅ Using weighted sampling for {dataset.split} set")
    
    # Create DataLoader
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        sampler=sampler,
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=True if num_workers > 0 else False,  # Faster on M2
        prefetch_factor=2 if num_workers > 0 else None  # Pre-load 2 batches
    )
    
    return dataloader


def create_dataloaders(
    metadata_path: str,
    data_dir: str,
    train_transform,
    valid_transform,
    batch_size: int = 32,
    use_weighted_sampling: bool = True,
    num_workers: int = 2
) -> dict:
    """
    Create train, val, and test dataloaders in one call.
    
    Args:
        metadata_path: Path to metadata.csv
        data_dir: Path to processed data directory
        train_transform: Augmentation pipeline for training
        valid_transform: Minimal transforms for val/test
        batch_size: Batch size for all loaders
        use_weighted_sampling: Use weighted sampling for training
        num_workers: Number of workers
        
    Returns:
        Dictionary with 'train', 'val', 'test' dataloaders
    """
    from ml.src.data.dataset import HAM10000Dataset
    
    print("="*60)
    print("🏗️  Creating DataLoaders")
    print("="*60)
    
    # Create datasets
    print("\n📂 Loading datasets...")
    train_dataset = HAM10000Dataset(
        metadata_path=metadata_path,
        data_dir=data_dir,
        split='train',
        transform=train_transform
    )
    
    val_dataset = HAM10000Dataset(
        metadata_path=metadata_path,
        data_dir=data_dir,
        split='val',
        transform=valid_transform
    )
    
    test_dataset = HAM10000Dataset(
        metadata_path=metadata_path,
        data_dir=data_dir,
        split='test',
        transform=valid_transform
    )
    
    # Create dataloaders
    print("\n⚙️  Creating DataLoaders...")
    train_loader = get_dataloader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        use_weighted_sampling=use_weighted_sampling,
        num_workers=num_workers,
        pin_memory=True
    )
    
    val_loader = get_dataloader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        use_weighted_sampling=False,  # No sampling for validation
        num_workers=num_workers,
        pin_memory=True
    )
    
    test_loader = get_dataloader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        use_weighted_sampling=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    print(f"\n✅ DataLoaders created:")
    print(f"   Train batches: {len(train_loader)} (batch_size={batch_size})")
    print(f"   Val batches:   {len(val_loader)}")
    print(f"   Test batches:  {len(test_loader)}")
    print("="*60)
    
    return {
        'train': train_loader,
        'val': val_loader,
        'test': test_loader,
        'datasets': {
            'train': train_dataset,
            'val': val_dataset,
            'test': test_dataset
        }
    }