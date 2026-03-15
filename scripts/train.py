"""
DermaVision — Training Script.

Entry point for two-phase model training:
  Phase 1: Freeze backbone → train classifier head (5 epochs)
  Phase 2: Unfreeze backbone → fine-tune entire model (20 epochs)
"""

import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch

from src.data.dataloader import create_dataloaders
from src.models.cnn_model import create_model
from src.models.loss import FocalLoss
from src.training.callbacks import EarlyStopping
from src.training.trainer import Trainer
from src.training.utils import load_config, seed_everything, get_device, count_parameters


def main():
    parser = argparse.ArgumentParser(description="DermaVision Training")
    parser.add_argument("--config", type=str, default="config/config.yaml",
                        help="Path to config file")
    parser.add_argument("--phase1_epochs", type=int, default=None,
                        help="Override Phase 1 epochs (frozen backbone)")
    parser.add_argument("--phase2_epochs", type=int, default=None,
                        help="Override Phase 2 epochs (fine-tune)")
    parser.add_argument("--batch_size", type=int, default=None,
                        help="Override batch size")
    parser.add_argument("--lr", type=float, default=None,
                        help="Override learning rate")
    parser.add_argument("--device", type=str, default="auto",
                        help="Device (auto, cuda, mps, cpu)")
    args = parser.parse_args()

    # Load config
    config = load_config(args.config)

    # Override with CLI arguments
    if args.phase1_epochs:
        config["training"]["phase1_epochs"] = args.phase1_epochs
    if args.phase2_epochs:
        config["training"]["phase2_epochs"] = args.phase2_epochs
    if args.batch_size:
        config["training"]["batch_size"] = args.batch_size
    if args.lr:
        config["training"]["learning_rate"] = args.lr

    phase1_epochs = config["training"]["phase1_epochs"]
    phase2_epochs = config["training"]["phase2_epochs"]

    # Reproducibility
    seed_everything(config["data"]["random_seed"])

    # Device
    device = get_device(args.device)

    print("\n🔬 DermaVision Training Pipeline")
    print("=" * 60)
    print(f"   Phase 1: {phase1_epochs} epochs (frozen backbone → classifier head)")
    print(f"   Phase 2: {phase2_epochs} epochs (full fine-tune)")

    # Data
    print("\n📦 Loading data...")
    dataloaders = create_dataloaders(
        metadata_path=config["data"]["metadata_path"],
        image_dir=config["data"]["processed_dir"],
        batch_size=config["training"]["batch_size"],
        image_size=config["data"]["image_size"],
        num_workers=config["training"]["num_workers"],
    )
    print(f"   Train: {len(dataloaders['train'].dataset):,} samples")
    print(f"   Val:   {len(dataloaders['val'].dataset):,} samples")
    print(f"   Test:  {len(dataloaders['test'].dataset):,} samples")

    # Model
    print("\n🧠 Building model...")
    model = create_model(
        num_classes=config["model"]["num_classes"],
        pretrained=config["model"]["pretrained"],
        dropout_rate=config["model"]["dropout_rate"],
        device=str(device),
    )
    params = count_parameters(model)
    print(f"   Architecture:     EfficientNet-B3")
    print(f"   Total params:     {params['total']:,}")
    print(f"   Trainable params: {params['trainable']:,}")
    print(f"   Model size:       {params['total_mb']:.1f} MB")

    # Loss function with class weights
    train_dataset = dataloaders["train"].dataset
    class_weights = torch.tensor(
        train_dataset.get_class_weights(), dtype=torch.float32
    ).to(device)
    criterion = FocalLoss(
        gamma=config["loss"]["gamma"],
        alpha=class_weights,
    )
    print(f"\n📉 Loss: Focal Loss (γ={config['loss']['gamma']})")

    # Optimizer: AdamW with lr=3e-4
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config["training"]["learning_rate"],
        weight_decay=config["training"]["weight_decay"],
    )
    print(f"   Optimizer: AdamW (lr={config['training']['learning_rate']})")

    # Scheduler: CosineAnnealingLR (resets per phase inside trainer)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=phase1_epochs,  # Phase 1 initially; trainer resets for Phase 2
        eta_min=1e-7,
    )

    # Callbacks
    callbacks = [
        EarlyStopping(
            patience=config["early_stopping"]["patience"],
            min_delta=config["early_stopping"]["min_delta"],
        ),
    ]
    print(f"   Early Stopping: patience={config['early_stopping']['patience']}")

    # Train (two-phase)
    trainer_config = {
        **config["training"],
        **config["logging"],
    }
    trainer = Trainer(
        model=model,
        criterion=criterion,
        optimizer=optimizer,
        scheduler=scheduler,
        device=str(device),
        config=trainer_config,
        callbacks=callbacks,
    )

    history = trainer.fit(
        train_loader=dataloaders["train"],
        val_loader=dataloaders["val"],
        phase1_epochs=phase1_epochs,
        phase2_epochs=phase2_epochs,
    )

    print(f"\n   Model saved to: models/best_model.pth")
    print(f"   Run evaluation: python scripts/evaluate.py\n")


if __name__ == "__main__":
    main()
