"""
DermaVision — Data Pipeline Tests.

Tests for dataset loading, augmentations, and data integrity.
"""

import os

import numpy as np
import pandas as pd
import pytest


class TestDermaDataset:
    """Tests for the DermaDataset class."""

    def test_class_mapping_completeness(self):
        """Verify all 7 HAM10000 classes are mapped."""
        from src.data.dataset import DermaDataset

        expected_classes = {"akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"}
        assert set(DermaDataset.DEFAULT_CLASS_MAP.keys()) == expected_classes

    def test_class_mapping_indices(self):
        """Verify class indices are 0-6."""
        from src.data.dataset import DermaDataset

        indices = set(DermaDataset.DEFAULT_CLASS_MAP.values())
        assert indices == {0, 1, 2, 3, 4, 5, 6}

    def test_class_weights_shape(self):
        """Verify class weights have correct shape."""
        from src.data.dataset import DermaDataset

        # Create mock data
        df = pd.DataFrame({
            "image_id": [f"img_{i}" for i in range(100)],
            "dx": np.random.choice(
                ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"],
                size=100,
            ),
        })
        dataset = DermaDataset(df, image_dir="/tmp", transform=None)
        weights = dataset.get_class_weights()

        assert weights.shape == (7,)
        assert np.all(weights > 0)


class TestAugmentations:
    """Tests for the augmentation pipelines."""

    def test_train_transform_output_shape(self):
        """Verify train transforms produce correct tensor shape."""
        from src.data.augmentations import get_train_transforms

        transform = get_train_transforms(image_size=224)
        dummy_image = np.random.randint(0, 255, (300, 400, 3), dtype=np.uint8)
        result = transform(image=dummy_image)

        assert result["image"].shape == (3, 224, 224)

    def test_val_transform_output_shape(self):
        """Verify val transforms produce correct tensor shape."""
        from src.data.augmentations import get_val_transforms

        transform = get_val_transforms(image_size=300)
        dummy_image = np.random.randint(0, 255, (450, 600, 3), dtype=np.uint8)
        result = transform(image=dummy_image)

        assert result["image"].shape == (3, 300, 300)

    def test_val_transform_deterministic(self):
        """Verify val transforms are deterministic."""
        from src.data.augmentations import get_val_transforms

        transform = get_val_transforms(image_size=224)
        dummy_image = np.random.randint(0, 255, (300, 400, 3), dtype=np.uint8)

        result1 = transform(image=dummy_image)["image"]
        result2 = transform(image=dummy_image)["image"]

        assert (result1 == result2).all()
