"""
DermaVision — Training Callbacks.

Early stopping and learning rate scheduler callbacks for training loop.
"""

import numpy as np
import torch
import torch.nn as nn


class EarlyStopping:
    """Early stopping to terminate training when validation loss plateaus.

    Args:
        patience: Number of epochs to wait before stopping.
        min_delta: Minimum improvement to qualify as progress.
        monitor: Metric to monitor ('val_loss').
        verbose: Whether to print status messages.

    Example:
        >>> early_stop = EarlyStopping(patience=10, min_delta=0.001)
        >>> callbacks = [early_stop]
    """

    def __init__(
        self,
        patience: int = 10,
        min_delta: float = 0.001,
        monitor: str = "val_loss",
        verbose: bool = True,
    ):
        self.patience = patience
        self.min_delta = min_delta
        self.monitor = monitor
        self.verbose = verbose

        self.counter = 0
        self.best_score = None
        self.best_model_weights = None

    def __call__(
        self, val_loss: float, model: nn.Module, epoch: int
    ) -> str | None:
        """Check if training should stop.

        Args:
            val_loss: Current validation loss.
            model: Model instance.
            epoch: Current epoch number.

        Returns:
            'stop' if training should stop, None otherwise.
        """
        score = -val_loss

        if self.best_score is None:
            self.best_score = score
            self.best_model_weights = model.state_dict().copy()
        elif score < self.best_score + self.min_delta:
            self.counter += 1
            if self.verbose:
                print(
                    f"  ⏳ EarlyStopping: {self.counter}/{self.patience} "
                    f"(no improvement)"
                )
            if self.counter >= self.patience:
                # Restore best weights
                model.load_state_dict(self.best_model_weights)
                return "stop"
        else:
            self.best_score = score
            self.best_model_weights = model.state_dict().copy()
            self.counter = 0

        return None


class LRSchedulerCallback:
    """Learning rate scheduler callback wrapper.

    Wraps PyTorch schedulers to integrate with the callback system.

    Args:
        scheduler: PyTorch LR scheduler instance.
        monitor: Metric to monitor (for ReduceLROnPlateau).

    Example:
        >>> scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=50)
        >>> callback = LRSchedulerCallback(scheduler)
    """

    def __init__(self, scheduler, monitor: str = "val_loss"):
        self.scheduler = scheduler
        self.monitor = monitor

    def __call__(
        self, val_loss: float, model: nn.Module, epoch: int
    ) -> None:
        """Step the scheduler.

        Args:
            val_loss: Current validation loss.
            model: Model instance (unused).
            epoch: Current epoch number.
        """
        if isinstance(
            self.scheduler,
            torch.optim.lr_scheduler.ReduceLROnPlateau,
        ):
            self.scheduler.step(val_loss)
        else:
            self.scheduler.step()
