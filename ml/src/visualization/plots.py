"""
DermaVision - Visualization Utilities.

Training curves, confusion matrices, and class distribution plots
for model analysis and reporting.
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import confusion_matrix as sk_confusion_matrix


def plot_training_curves(
    history: dict,
    save_path: str | None = None,
    figsize: tuple = (14, 5),
) -> plt.Figure:
    """Plot training and validation loss/accuracy curves.

    Args:
        history: Training history dict with 'loss', 'val_loss', 'val_metrics'.
        save_path: Optional path to save the figure.
        figsize: Figure size.

    Returns:
        Matplotlib figure.
    """
    fig, axes = plt.subplots(1, 3, figsize=figsize)

    epochs = range(1, len(history["loss"]) + 1)

    # Loss curves
    axes[0].plot(epochs, history["loss"], "b-", label="Train Loss", linewidth=2)
    axes[0].plot(epochs, history["val_loss"], "r-", label="Val Loss", linewidth=2)
    axes[0].set_title("Loss Curves", fontsize=14, fontweight="bold")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Loss")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Accuracy curves
    val_acc = [m["accuracy"] for m in history.get("val_metrics", [])]
    if val_acc:
        axes[1].plot(epochs[:len(val_acc)], val_acc, "g-", label="Accuracy", linewidth=2)
        bal_acc = [m["balanced_accuracy"] for m in history["val_metrics"]]
        axes[1].plot(epochs[:len(bal_acc)], bal_acc, "m-", label="Balanced Acc", linewidth=2)
        axes[1].set_title("Accuracy Curves", fontsize=14, fontweight="bold")
        axes[1].set_xlabel("Epoch")
        axes[1].set_ylabel("Accuracy")
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

    # F1 curves
    f1_scores = [m["weighted_f1"] for m in history.get("val_metrics", [])]
    if f1_scores:
        axes[2].plot(epochs[:len(f1_scores)], f1_scores, "c-", label="Weighted F1", linewidth=2)
        macro_f1 = [m["macro_f1"] for m in history["val_metrics"]]
        axes[2].plot(epochs[:len(macro_f1)], macro_f1, "y-", label="Macro F1", linewidth=2)
        axes[2].set_title("F1 Score Curves", fontsize=14, fontweight="bold")
        axes[2].set_xlabel("Epoch")
        axes[2].set_ylabel("F1 Score")
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")

    return fig


def plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: list[str] | None = None,
    normalize: bool = True,
    save_path: str | None = None,
    figsize: tuple = (10, 8),
) -> plt.Figure:
    """Plot a styled confusion matrix heatmap.

    Args:
        y_true: Ground truth labels.
        y_pred: Predicted labels.
        class_names: Class names for axis labels.
        normalize: Whether to normalize by row (recall).
        save_path: Optional path to save the figure.
        figsize: Figure size.

    Returns:
        Matplotlib figure.
    """
    if class_names is None:
        class_names = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]

    cm = sk_confusion_matrix(y_true, y_pred)

    if normalize:
        cm_display = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
        fmt = ".2f"
        title = "Normalized Confusion Matrix"
    else:
        cm_display = cm
        fmt = "d"
        title = "Confusion Matrix"

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(
        cm_display,
        annot=True,
        fmt=fmt,
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
        square=True,
        linewidths=0.5,
        ax=ax,
    )

    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
    ax.set_xlabel("Predicted Label", fontsize=12)
    ax.set_ylabel("True Label", fontsize=12)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")

    return fig


def plot_class_distribution(
    distribution: dict,
    save_path: str | None = None,
    figsize: tuple = (10, 6),
) -> plt.Figure:
    """Plot class distribution as a bar chart.

    Args:
        distribution: Dictionary of {class_name: count}.
        save_path: Optional path to save.
        figsize: Figure size.

    Returns:
        Matplotlib figure.
    """
    fig, ax = plt.subplots(figsize=figsize)

    classes = list(distribution.keys())
    counts = list(distribution.values())
    colors = sns.color_palette("husl", len(classes))

    bars = ax.bar(classes, counts, color=colors, edgecolor="white", linewidth=1.5)

    # Add count labels on bars
    for bar, count in zip(bars, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(counts) * 0.01,
            str(count),
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    ax.set_title("Class Distribution", fontsize=16, fontweight="bold")
    ax.set_xlabel("Diagnosis", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")

    return fig
