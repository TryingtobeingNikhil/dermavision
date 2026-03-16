"""
Test the complete data pipeline.
"""

from pathlib import Path
import sys

import torch
import matplotlib.pyplot as plt

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from ml.src.data.augmentations import get_train_transforms, get_valid_transforms
from ml.src.data.dataloader import create_dataloaders


def test_pipeline():
    """Test data pipeline and visualize batches."""
    
    print("Testing Complete Data Pipeline\n")
    
    # Create dataloaders
    loaders = create_dataloaders(
        metadata_path='data/metadata.csv',
        data_dir='data/processed',
        train_transform=get_train_transforms(image_size=224),
        valid_transform=get_valid_transforms(image_size=224),
        batch_size=32,
        use_weighted_sampling=True,
        num_workers=2
    )
    
    train_loader = loaders['train']
    val_loader = loaders['val']
    
    # Test batch loading
    print("\n🔍 Testing batch loading...")
    batch = next(iter(train_loader))
    
    print(f"   Batch image shape: {batch['image'].shape}")
    print(f"   Batch label shape: {batch['label'].shape}")
    print(f"   Image dtype: {batch['image'].dtype}")
    print(f"   Label dtype: {batch['label'].dtype}")
    print(f"   Image range: [{batch['image'].min():.3f}, {batch['image'].max():.3f}]")
    
    # Check class distribution in a batch (with weighted sampling)
    print("\n📊 Class distribution in batch (weighted sampling):")
    labels = batch['label'].numpy()
    unique, counts = torch.unique(batch['label'], return_counts=True)
    
    from ml.src.data.dataset import HAM10000Dataset
    for label, count in zip(unique, counts):
        class_name = HAM10000Dataset.IDX_TO_CLASS[label.item()]
        print(f"   {class_name:6s}: {count:2d} samples")
    
    print("\n✅ Pipeline test passed!")
    print("\n💡 Next: Visualize augmented samples in notebook")
    

if __name__ == "__main__":
    test_pipeline()