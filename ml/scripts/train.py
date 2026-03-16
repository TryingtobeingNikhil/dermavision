"""
Main training script.

Usage:
    python scripts/train.py
"""

import sys
from pathlib import Path

# Add repository root to path so ml.src imports work when run from repo root
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

import torch
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR

from ml.src.data.augmentations import get_train_transforms, get_valid_transforms
from ml.src.data.dataloader import create_dataloaders
from ml.src.models.cnn_model import create_model
from ml.src.models.loss import create_loss_function
from ml.src.training.trainer import Trainer


def main():
    """Main training function."""
    
    # Device setup
    if torch.backends.mps.is_available():
        device = 'mps'
    elif torch.cuda.is_available():
        device = 'cuda'
    else:
        device = 'cpu'
    
    print(f"Using device: {device}")
    
    # Hyperparameters
    config = {
        # Data
        "image_size": 256,
        "batch_size": 64,
        "num_workers": 2,

        # Training
        "num_epochs": 35,
        "learning_rate": 3e-4,
        "weight_decay": 1e-4,

        # Loss (for class imbalance)
        "loss_type": "focal",
        "focal_gamma": 2.0,
        "label_smoothing": 0.1,

        # Sampling
        "use_weighted_sampling": True,

        # Early stopping
        "patience": 10,

        # LR Scheduler
        "scheduler": "ReduceLROnPlateau",
        "lr_factor": 0.3,
        "lr_patience": 3,

        # Model
        "model_name": "efficientnet_b3",
        "pretrained": True,

        # Mixed precision (auto-disabled on non-CUDA)
        "use_amp": True,
    }
    
    print("\nConfiguration:")
    for k, v in config.items():
        print(f"  {k}: {v}")
    
    # Create dataloaders
    data_root = repo_root / 'data'
    loaders = create_dataloaders(
        metadata_path=str(data_root / 'metadata.csv'),
        data_dir=str(data_root / 'processed'),
        train_transform=get_train_transforms(image_size=config['image_size']),
        valid_transform=get_valid_transforms(image_size=config['image_size']),
        batch_size=config['batch_size'],
        use_weighted_sampling=config['use_weighted_sampling'],
        num_workers=config['num_workers']
    )
    
    train_loader = loaders['train']
    val_loader = loaders['val']
    train_dataset = loaders['datasets']['train']
    
    # Create model
    model = create_model(
        num_classes=7,
        pretrained=True,
        dropout=0.3,
        freeze_backbone=True,  # Start with frozen backbone
        device=device
    )
    
    # Get class weights
    class_weights = train_dataset.get_class_weights().to(device)
    
    # Create loss function
    criterion = create_loss_function(
        loss_type=config['loss_type'],
        class_weights=class_weights,
        gamma=config['focal_gamma'],
        label_smoothing=config['label_smoothing']
    )
    
    # Optimizer
    optimizer = optim.AdamW(
        model.parameters(),
        lr=config['learning_rate'],
        weight_decay=config['weight_decay']
    )
    
    # Learning rate scheduler
    scheduler = CosineAnnealingLR(
        optimizer,
        T_max=config['num_epochs'],
        eta_min=1e-6
    )
    
    # Create trainer (save under ml/models and ml/logs)
    ml_root = repo_root / 'ml'
    trainer = Trainer(
        model=model,
        criterion=criterion,
        optimizer=optimizer,
        device=device,
        checkpoint_dir=str(ml_root / 'models'),
        log_dir=str(ml_root / 'logs'),
        use_amp=config['use_amp']
    )
    
    # Phase 1: Train only classifier head
    print("\n" + "="*60)
    print("PHASE 1: Training classifier head only (5 epochs)")
    print("="*60)
    
    trainer.fit(
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=5,
        patience=config['patience'],
        scheduler=scheduler
    )
    
    # Phase 2: Unfreeze and fine-tune full model
    print("\n" + "="*60)
    print("PHASE 2: Fine-tuning full model")
    print("="*60)
    
    model.unfreeze_backbone()
    
    # Lower learning rate for fine-tuning
    for param_group in optimizer.param_groups:
        param_group['lr'] = 5e-5
    
    # Reset scheduler
    scheduler = CosineAnnealingLR(
        optimizer,
        T_max=config['num_epochs'] - 5,
        eta_min=1e-7
    )
    
    trainer.fit(
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=config['num_epochs'] - 5,
        patience=config['patience'],
        scheduler=scheduler
    )
    
    print("\n🎉 Training complete! Check the 'ml/models/' directory for checkpoints.")


if __name__ == '__main__':
    main()