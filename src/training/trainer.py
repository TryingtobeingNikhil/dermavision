"""
DermaVision — Training Loop.

Two-phase training pipeline:
  Phase 1: Freeze backbone, train only classifier head (warmup)
  Phase 2: Unfreeze backbone, fine-tune entire model

Includes mixed precision, TensorBoard logging, and checkpoint management.
"""

import os
import time

import numpy as np
import torch
import torch.nn as nn
from torch.cuda.amp import GradScaler, autocast
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm

from ..models.metrics import compute_metrics


class Trainer:
    """Two-phase training orchestrator for DermaVision model.

    Phase 1: Backbone frozen → train classifier head only.
    Phase 2: Full model unfrozen → fine-tune everything with lower LR.

    Args:
        model: PyTorch model (must have freeze_backbone method).
        criterion: Loss function.
        optimizer: Optimizer instance.
        scheduler: Learning rate scheduler (optional).
        device: Training device.
        config: Configuration dictionary.
        callbacks: List of callback instances.

    Example:
        >>> trainer = Trainer(model, criterion, optimizer, scheduler, device, config)
        >>> trainer.fit(train_loader, val_loader, phase1_epochs=5, phase2_epochs=20)
    """

    def __init__(
        self,
        model: nn.Module,
        criterion: nn.Module,
        optimizer: torch.optim.Optimizer,
        scheduler=None,
        device: str = "cuda",
        config: dict | None = None,
        callbacks: list | None = None,
    ):
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.device = device
        self.config = config or {}
        self.callbacks = callbacks or []

        # Mixed precision
        self.use_amp = self.config.get("mixed_precision", True) and device == "cuda"
        self.scaler = GradScaler() if self.use_amp else None

        # Logging
        log_dir = self.config.get("tensorboard_dir", "logs/tensorboard")
        self.writer = SummaryWriter(log_dir)

        # State tracking
        self.best_val_auc = 0.0
        self.best_val_loss = float("inf")
        self.current_epoch = 0
        self.global_epoch = 0  # Tracks across both phases
        self.train_history = {"loss": [], "val_loss": [], "val_metrics": []}

    def fit(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        phase1_epochs: int = 5,
        phase2_epochs: int = 20,
    ) -> dict:
        """Run two-phase training.

        Phase 1: Frozen backbone — trains classifier head only.
        Phase 2: Unfrozen — fine-tunes the entire model.

        Args:
            train_loader: Training DataLoader.
            val_loader: Validation DataLoader.
            phase1_epochs: Epochs for Phase 1 (frozen backbone).
            phase2_epochs: Epochs for Phase 2 (full fine-tune).

        Returns:
            Training history dictionary.
        """
        total_epochs = phase1_epochs + phase2_epochs

        print(f"\n{'='*60}")
        print(f"  DermaVision Two-Phase Training")
        print(f"  Phase 1: {phase1_epochs} epochs (frozen backbone)")
        print(f"  Phase 2: {phase2_epochs} epochs (full fine-tune)")
        print(f"  Device: {self.device} | AMP: {self.use_amp}")
        print(f"{'='*60}")

        # ── Phase 1: Frozen backbone ──────────────────────────────
        print(f"\n🧊 Phase 1 — Training classifier head only")
        print(f"{'─'*60}")
        self.model.freeze_backbone(True)

        for epoch in range(phase1_epochs):
            self.global_epoch = epoch
            stop = self._run_epoch(
                train_loader, val_loader, epoch, total_epochs, phase=1
            )
            if stop:
                print(f"\n⏹  Early stopping in Phase 1 at epoch {epoch + 1}")
                break

        # ── Phase 2: Full fine-tune ───────────────────────────────
        print(f"\n🔥 Phase 2 — Fine-tuning entire model")
        print(f"{'─'*60}")
        self.model.freeze_backbone(False)

        # Reset callbacks for phase 2
        for callback in self.callbacks:
            if hasattr(callback, "counter"):
                callback.counter = 0
                callback.best_score = None

        # Reset scheduler for phase 2
        if self.scheduler:
            self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer,
                T_max=phase2_epochs,
                eta_min=1e-7,
            )

        for epoch in range(phase2_epochs):
            global_ep = phase1_epochs + epoch
            self.global_epoch = global_ep
            stop = self._run_epoch(
                train_loader, val_loader, global_ep, total_epochs, phase=2
            )
            if stop:
                print(f"\n⏹  Early stopping in Phase 2 at epoch {global_ep + 1}")
                break

        self.writer.close()

        print(f"\n{'='*60}")
        print(f"✅ Training complete!")
        print(f"   Best val AUC: {self.best_val_auc:.4f}")
        print(f"   Best val loss: {self.best_val_loss:.4f}")
        print(f"{'='*60}")

        return self.train_history

    def _run_epoch(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epoch: int,
        total_epochs: int,
        phase: int,
    ) -> bool:
        """Run a single training + validation epoch.

        Returns:
            True if early stopping triggered, False otherwise.
        """
        # Train
        train_loss = self._train_epoch(train_loader, epoch, total_epochs, phase)

        # Validate
        val_loss, val_metrics = self._validate_epoch(val_loader, epoch, total_epochs, phase)

        # Log
        self._log_epoch(epoch, train_loss, val_loss, val_metrics, phase)

        # Save best model (by val AUC)
        val_auc = val_metrics.get("auc_roc_macro") or 0.0
        if val_auc > self.best_val_auc:
            self.best_val_auc = val_auc
            self._save_checkpoint(epoch, val_loss, val_auc, is_best=True)

        if val_loss < self.best_val_loss:
            self.best_val_loss = val_loss
            # Also save by best loss if AUC unavailable
            if val_auc == 0.0:
                self._save_checkpoint(epoch, val_loss, val_auc, is_best=True)

        # Callbacks (early stopping checks)
        stop = False
        for callback in self.callbacks:
            result = callback(val_loss, self.model, epoch)
            if result == "stop":
                stop = True

        # Scheduler step
        if self.scheduler:
            if isinstance(self.scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                self.scheduler.step(val_loss)
            else:
                self.scheduler.step()

        return stop

    def _train_epoch(
        self, loader: DataLoader, epoch: int, total_epochs: int, phase: int
    ) -> float:
        """Execute one training epoch."""
        self.model.train()
        running_loss = 0.0
        num_batches = 0

        phase_label = "Head" if phase == 1 else "Fine-tune"
        pbar = tqdm(
            loader,
            desc=f"Epoch {epoch+1}/{total_epochs} [{phase_label}]",
            leave=False,
        )

        for images, labels in pbar:
            images = images.to(self.device)
            labels = labels.to(self.device)

            self.optimizer.zero_grad()

            if self.use_amp:
                with autocast():
                    outputs = self.model(images)
                    loss = self.criterion(outputs, labels)
                self.scaler.scale(loss).backward()
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                loss.backward()
                self.optimizer.step()

            running_loss += loss.item()
            num_batches += 1
            pbar.set_postfix({"loss": f"{loss.item():.4f}"})

        avg_loss = running_loss / max(num_batches, 1)
        self.train_history["loss"].append(avg_loss)
        return avg_loss

    @torch.no_grad()
    def _validate_epoch(
        self, loader: DataLoader, epoch: int, total_epochs: int, phase: int
    ) -> tuple[float, dict]:
        """Execute one validation epoch."""
        self.model.eval()
        running_loss = 0.0
        num_batches = 0
        all_preds, all_labels, all_probs = [], [], []

        phase_label = "Head" if phase == 1 else "Fine-tune"
        pbar = tqdm(
            loader,
            desc=f"Epoch {epoch+1}/{total_epochs} [{phase_label} Val]",
            leave=False,
        )

        for images, labels in pbar:
            images = images.to(self.device)
            labels = labels.to(self.device)

            outputs = self.model(images)
            loss = self.criterion(outputs, labels)

            running_loss += loss.item()
            num_batches += 1

            probs = torch.softmax(outputs, dim=1)
            preds = probs.argmax(dim=1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())

        avg_loss = running_loss / max(num_batches, 1)
        self.train_history["val_loss"].append(avg_loss)

        # Compute metrics
        metrics = compute_metrics(
            np.array(all_labels),
            np.array(all_preds),
            np.array(all_probs),
        )
        self.train_history["val_metrics"].append(metrics)

        return avg_loss, metrics

    def _log_epoch(
        self, epoch: int, train_loss: float, val_loss: float,
        metrics: dict, phase: int
    ) -> None:
        """Log metrics to TensorBoard and console."""
        # TensorBoard
        self.writer.add_scalar("Loss/train", train_loss, epoch)
        self.writer.add_scalar("Loss/val", val_loss, epoch)
        self.writer.add_scalar("Metrics/accuracy", metrics["accuracy"], epoch)
        self.writer.add_scalar("Metrics/balanced_accuracy", metrics["balanced_accuracy"], epoch)
        self.writer.add_scalar("Metrics/weighted_f1", metrics["weighted_f1"], epoch)

        if metrics.get("auc_roc_macro"):
            self.writer.add_scalar("Metrics/auc_roc_macro", metrics["auc_roc_macro"], epoch)

        # Melanoma sensitivity
        mel_sens = metrics.get("per_class", {}).get("mel", {}).get("sensitivity", 0.0)
        self.writer.add_scalar("Metrics/melanoma_sensitivity", mel_sens, epoch)

        lr = self.optimizer.param_groups[0]["lr"]
        self.writer.add_scalar("LR", lr, epoch)
        self.writer.add_scalar("Phase", phase, epoch)

        # Console
        auc_str = f"AUC: {metrics.get('auc_roc_macro', 0):.4f} | " if metrics.get("auc_roc_macro") else ""
        phase_tag = "🧊" if phase == 1 else "🔥"
        print(
            f"  {phase_tag} Epoch {epoch+1:3d} | "
            f"Train: {train_loss:.4f} | "
            f"Val: {val_loss:.4f} | "
            f"Acc: {metrics['accuracy']:.4f} | "
            f"{auc_str}"
            f"Mel Sens: {mel_sens:.4f} | "
            f"LR: {lr:.6f}"
        )

    def _save_checkpoint(
        self, epoch: int, val_loss: float, val_auc: float,
        is_best: bool = False
    ) -> None:
        """Save model checkpoint."""
        save_dir = self.config.get("save_dir", "models")
        os.makedirs(save_dir, exist_ok=True)

        checkpoint = {
            "epoch": epoch,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "val_loss": val_loss,
            "val_auc": val_auc,
            "config": self.config,
        }

        if is_best:
            path = os.path.join(save_dir, "best_model.pth")
            torch.save(checkpoint, path)
            print(f"  ✅ Best model saved (AUC: {val_auc:.4f}, loss: {val_loss:.4f})")
