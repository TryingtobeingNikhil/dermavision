"""
Main training script.

Usage:
    python scripts/train.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import torch
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR

from src.data.augmentations import get_train_transforms, get_valid_transforms
from src.data.dataloader import create_dataloaders
from src.models.cnn_model import create_model
from src.models.loss import create_loss_function
from src.training.trainer import Trainer


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
        'batch_size': 32,
        'num_epochs': 25,
        'learning_rate': 3e-4,
        'weight_decay': 1e-4,
        'patience': 7,
        'image_size': 224,
        'num_workers': 2,
        'use_weighted_sampling': True,
        'loss_type': 'focal',
        'focal_gamma': 2.0,
    }
    
    print("\nConfiguration:")
    for k, v in config.items():
        print(f"  {k}: {v}")
    
    # Create dataloaders
    loaders = create_dataloaders(
        metadata_path='data/metadata.csv',
        data_dir='data/processed',
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
        gamma=config['focal_gamma']
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
    
    # Create trainer
    trainer = Trainer(
        model=model,
        criterion=criterion,
        optimizer=optimizer,
        device=device,
        checkpoint_dir='models',
        log_dir='logs'
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
        param_group['lr'] = 1e-5
    
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
    
    print("\n🎉 Training complete! Check the 'models/' directory for checkpoints.")


if __name__ == '__main__':
    main()