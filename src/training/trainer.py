"""
Training loop for skin lesion classifier.

Handles training, validation, checkpointing, and logging.
"""

import torch
from torch.amp import autocast, GradScaler
import torch.nn as nn
from torch.utils.data import DataLoader
from pathlib import Path
import time
from tqdm import tqdm
import json

from src.models.metrics import MetricsCalculator
from src.data.dataset import HAM10000Dataset


class Trainer:
    """
    Manages the training and validation loop.
    
    Takes care of:
    - Forward/backward passes
    - Metric tracking
    - Model checkpointing
    - Early stopping
    - Learning rate scheduling
    """
    
    def __init__(
        self,
        model: nn.Module,
        criterion: nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str,
        checkpoint_dir: str = 'models',
        log_dir: str = 'logs',
        use_amp: bool = False
    ):
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.device = device
        
        # Mixed precision training (AMP)
        self.use_amp = use_amp and device == 'cuda'
        self.scaler = GradScaler('cuda', enabled=self.use_amp)
        
        # Create directories
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Training state
        self.current_epoch = 0
        self.best_val_loss = float('inf')
        self.best_val_f1 = 0.0
        self.train_losses = []
        self.val_losses = []
        self.train_metrics = []
        self.val_metrics = []
        
        # Early stopping
        self.patience_counter = 0
        
        print("✅ Trainer initialized")
        print(f"   Device: {device}")
        print(f"   Mixed Precision: {'✅ Enabled' if self.use_amp else '❌ Disabled'}")
        print(f"   Checkpoints: {self.checkpoint_dir}")
        print(f"   Logs: {self.log_dir}")
    
    def train_epoch(self, train_loader: DataLoader) -> dict:
        """Run one training epoch."""
        self.model.train()
        
        running_loss = 0.0
        metrics_calc = MetricsCalculator(
            num_classes=7,
            class_names={i: HAM10000Dataset.FULL_NAMES[HAM10000Dataset.IDX_TO_CLASS[i]] 
                        for i in range(7)}
        )
        
        pbar = tqdm(train_loader, desc=f'Epoch {self.current_epoch+1} [Train]')
        
        for batch in pbar:
            images = batch['image'].to(self.device)
            labels = batch['label'].to(self.device)
            
            # Forward pass with AMP
            self.optimizer.zero_grad()
            with autocast('cuda', enabled=self.use_amp):
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
            
            # Backward pass with gradient scaling
            self.scaler.scale(loss).backward()
            self.scaler.step(self.optimizer)
            self.scaler.update()
            
            # Track metrics
            running_loss += loss.item() * images.size(0)
            
            probs = torch.softmax(outputs.float(), dim=1)
            preds = torch.argmax(probs, dim=1)
            
            metrics_calc.update(preds, labels, probs)
            
            # Update progress bar
            pbar.set_postfix({'loss': f'{loss.item():.4f}'})
        
        # Calculate epoch metrics
        epoch_loss = running_loss / len(train_loader.dataset)
        epoch_metrics = metrics_calc.compute()
        
        return {
            'loss': epoch_loss,
            'metrics': epoch_metrics
        }
    
    def validate(self, val_loader: DataLoader) -> dict:
        """Run validation."""
        self.model.eval()
        
        running_loss = 0.0
        metrics_calc = MetricsCalculator(
            num_classes=7,
            class_names={i: HAM10000Dataset.FULL_NAMES[HAM10000Dataset.IDX_TO_CLASS[i]] 
                        for i in range(7)}
        )
        
        pbar = tqdm(val_loader, desc=f'Epoch {self.current_epoch+1} [Val]  ')
        
        with torch.no_grad():
            for batch in pbar:
                images = batch['image'].to(self.device)
                labels = batch['label'].to(self.device)
                
                with autocast('cuda', enabled=self.use_amp):
                    outputs = self.model(images)
                    loss = self.criterion(outputs, labels)
                
                running_loss += loss.item() * images.size(0)
                
                probs = torch.softmax(outputs.float(), dim=1)
                preds = torch.argmax(probs, dim=1)
                
                metrics_calc.update(preds, labels, probs)
                
                pbar.set_postfix({'loss': f'{loss.item():.4f}'})
        
        epoch_loss = running_loss / len(val_loader.dataset)
        epoch_metrics = metrics_calc.compute()
        
        return {
            'loss': epoch_loss,
            'metrics': epoch_metrics
        }
    
    def save_checkpoint(self, is_best: bool = False, filename: str = None):
        """Save model checkpoint."""
        if filename is None:
            filename = f'checkpoint_epoch_{self.current_epoch}.pth'
        
        checkpoint_path = self.checkpoint_dir / filename
        
        checkpoint = {
            'epoch': self.current_epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'best_val_loss': self.best_val_loss,
            'best_val_f1': self.best_val_f1,
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
        }
        
        torch.save(checkpoint, checkpoint_path)
        
        if is_best:
            best_path = self.checkpoint_dir / 'best_model.pth'
            torch.save(checkpoint, best_path)
            print(f"   💾 Saved best model to {best_path}")
    
    def fit(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int,
        patience: int = 5,
        scheduler=None
    ):
        """
        Main training loop.
        
        Args:
            train_loader: Training data
            val_loader: Validation data
            epochs: Number of epochs
            patience: Early stopping patience
            scheduler: Learning rate scheduler (optional)
        """
        print("\n" + "="*60)
        print("🚀 Starting Training")
        print("="*60)
        
        start_time = time.time()
        
        for epoch in range(epochs):
            self.current_epoch = epoch
            
            # Train
            train_results = self.train_epoch(train_loader)
            self.train_losses.append(train_results['loss'])
            self.train_metrics.append(train_results['metrics'])
            
            # Validate
            val_results = self.validate(val_loader)
            self.val_losses.append(val_results['loss'])
            self.val_metrics.append(val_results['metrics'])
            
            # Print epoch summary
            print(f"\nEpoch {epoch+1}/{epochs}")
            print(f"  Train - Loss: {train_results['loss']:.4f} | "
                  f"F1: {train_results['metrics']['macro_f1']:.4f} | "
                  f"Acc: {train_results['metrics']['accuracy']:.4f}")
            print(f"  Val   - Loss: {val_results['loss']:.4f} | "
                  f"F1: {val_results['metrics']['macro_f1']:.4f} | "
                  f"Acc: {val_results['metrics']['accuracy']:.4f}")
            print(f"  Melanoma Sensitivity: {val_results['metrics']['melanoma_sensitivity']:.4f}")
            
            # Check for improvement
            val_f1 = val_results['metrics']['macro_f1']
            is_best = val_f1 > self.best_val_f1
            
            if is_best:
                self.best_val_f1 = val_f1
                self.best_val_loss = val_results['loss']
                self.patience_counter = 0
                self.save_checkpoint(is_best=True)
            else:
                self.patience_counter += 1
            
            # Learning rate scheduling
            if scheduler:
                scheduler.step()
                current_lr = self.optimizer.param_groups[0]['lr']
                print(f"  Learning rate: {current_lr:.6f}")
            
            # Early stopping check
            if self.patience_counter >= patience:
                print(f"\n⚠️  Early stopping triggered (no improvement for {patience} epochs)")
                break
            
            # Save periodic checkpoint
            if (epoch + 1) % 5 == 0:
                self.save_checkpoint(filename=f'checkpoint_epoch_{epoch+1}.pth')
        
        total_time = time.time() - start_time
        
        print("\n" + "="*60)
        print("✅ Training Complete")
        print("="*60)
        print(f"Total time: {total_time/60:.2f} minutes")
        print(f"Best Val F1: {self.best_val_f1:.4f}")
        print(f"Best Val Loss: {self.best_val_loss:.4f}")
        print("="*60)
        
        # Save training history
        history = {
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'train_metrics': [
                {k: float(v) if isinstance(v, (int, float)) else v 
                 for k, v in m.items()} 
                for m in self.train_metrics
            ],
            'val_metrics': [
                {k: float(v) if isinstance(v, (int, float)) else v 
                 for k, v in m.items()} 
                for m in self.val_metrics
            ],
        }
        
        history_path = self.log_dir / 'training_history.json'
        with open(history_path, 'w') as f:
            json.dump(history, f, indent=2)
        
        print(f"📊 Training history saved to {history_path}")