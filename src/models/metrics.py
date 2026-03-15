"""
DermaVision — Custom Evaluation Metrics.

Provides medical-domain metrics: sensitivity, specificity, balanced accuracy,
and per-class performance optimized for dermatological classification.
"""

import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    cohen_kappa_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray | None = None,
    class_names: list[str] | None = None,
) -> dict:
    """Compute comprehensive classification metrics.

    Args:
        y_true: Ground truth labels of shape (N,).
        y_pred: Predicted labels of shape (N,).
        y_prob: Predicted probabilities of shape (N, C) for AUC computation.
        class_names: List of class names for the report.

    Returns:
        Dictionary containing all computed metrics.
    """
    if class_names is None:
        class_names = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]

    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "weighted_f1": f1_score(y_true, y_pred, average="weighted"),
        "macro_f1": f1_score(y_true, y_pred, average="macro"),
        "weighted_precision": precision_score(y_true, y_pred, average="weighted"),
        "weighted_recall": recall_score(y_true, y_pred, average="weighted"),
        "cohen_kappa": cohen_kappa_score(y_true, y_pred),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }

    # Per-class sensitivity and specificity
    cm = np.array(metrics["confusion_matrix"])
    per_class = {}
    for i, name in enumerate(class_names):
        tp = cm[i, i]
        fn = cm[i, :].sum() - tp
        fp = cm[:, i].sum() - tp
        tn = cm.sum() - tp - fn - fp

        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0

        per_class[name] = {
            "sensitivity": round(sensitivity, 4),
            "specificity": round(specificity, 4),
            "support": int(tp + fn),
        }

    metrics["per_class"] = per_class

    # AUC-ROC (if probabilities provided)
    if y_prob is not None:
        try:
            metrics["auc_roc_macro"] = roc_auc_score(
                y_true, y_prob, multi_class="ovr", average="macro"
            )
            metrics["auc_roc_weighted"] = roc_auc_score(
                y_true, y_prob, multi_class="ovr", average="weighted"
            )
        except ValueError:
            metrics["auc_roc_macro"] = None
            metrics["auc_roc_weighted"] = None

    # Full classification report
    metrics["classification_report"] = classification_report(
        y_true, y_pred, target_names=class_names, output_dict=True
    )

    return metrics


def sensitivity_at_specificity(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    target_specificity: float = 0.95,
    class_idx: int = 4,  # Melanoma
) -> float:
    """Compute sensitivity at a given specificity threshold.

    Important for melanoma detection where high specificity is crucial
    to minimize unnecessary biopsies while maintaining sensitivity.

    Args:
        y_true: Ground truth labels.
        y_prob: Predicted probabilities for the target class.
        target_specificity: Desired specificity threshold.
        class_idx: Target class index (default: 4 = melanoma).

    Returns:
        Sensitivity value at the target specificity.
    """
    binary_true = (y_true == class_idx).astype(int)
    probs = y_prob[:, class_idx] if y_prob.ndim > 1 else y_prob

    # Sort by decreasing probability
    sorted_indices = np.argsort(-probs)
    sorted_true = binary_true[sorted_indices]
    sorted_probs = probs[sorted_indices]

    n_positive = sorted_true.sum()
    n_negative = len(sorted_true) - n_positive

    best_sensitivity = 0.0

    for threshold in np.unique(sorted_probs):
        predicted_positive = probs >= threshold
        tp = (predicted_positive & (binary_true == 1)).sum()
        tn = (~predicted_positive & (binary_true == 0)).sum()

        sensitivity = tp / n_positive if n_positive > 0 else 0
        specificity = tn / n_negative if n_negative > 0 else 0

        if specificity >= target_specificity:
            best_sensitivity = max(best_sensitivity, sensitivity)

    return best_sensitivity
