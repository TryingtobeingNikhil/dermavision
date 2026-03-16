"""Quick test of the dataset class."""

from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from ml.src.data.dataset import HAM10000Dataset
from ml.src.data.augmentations import get_train_transforms, get_valid_transforms

# Test loading
print("Testing Dataset Loading...\n")

# Load train dataset
train_dataset = HAM10000Dataset(
    metadata_path='data/metadata.csv',
    data_dir='data/processed',
    split='train',
    transform=get_train_transforms(image_size=224)
)

# Load validation dataset
val_dataset = HAM10000Dataset(
    metadata_path='data/metadata.csv',
    data_dir='data/processed',
    split='val',
    transform=get_valid_transforms(image_size=224)
)

# Test getting a sample
print("\n🔍 Testing sample retrieval...")
sample = train_dataset[0]
print(f"   Image shape: {sample['image'].shape}")
print(f"   Label: {sample['label']} ({train_dataset.IDX_TO_CLASS[sample['label']]})")
print(f"   Image ID: {sample['image_id']}")

# Test class weights
print("\n⚖️  Computing class weights...")
weights = train_dataset.get_class_weights()

print("\n✅ All tests passed!")