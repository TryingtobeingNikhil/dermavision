"""
Evaluation Metrics for Medical Image Classification

Implements:
- Accuracy (overall and per-class)
- Sensitivity (Recall) - critical for melanoma
- Specificity - important for reducing false positives
- Precision
- F1 Score
- AUC-ROC (macro and weighted)
- Confusion Matrix utilities
"""

import torch
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    roc_auc_score,
    confusion_matrix
)
from typing import Dict, Tuple


class MetricsCalculator:
    """
    Calculate comprehensive metrics for multi-class classification.
    
    Special focus on melanoma (class 4) sensitivity.
    """
    
    def __init__(self, num_classes: int = 7, class_names: dict = None):
        """
        Initialize metrics calculator.
        
        Args:
            num_classes: Number of classes
            class_names: Dictionary mapping class indices to names
        """
        self.num_classes = num_classes
        self.class_names = class_names or {i: f"Class_{i}" for i in range(num_classes)}
        self.reset()
    
    def reset(self):
        """Reset all accumulators."""
        self.all_predictions = []
        self.all_targets = []
        self.all_probabilities = []
    
    def update(
        self,
        predictions: torch.Tensor,
        targets: torch.Tensor,
        probabilities: torch.Tensor = None
    ):
        """
        Update metrics with a batch.
        
        Args:
            predictions: Predicted class indices [batch_size]
            targets: Ground truth labels [batch_size]
            probabilities: Class probabilities [batch_size, num_classes] (optional)
        """
        self.all_predictions.extend(predictions.cpu().numpy())
        self.all_targets.extend(targets.cpu().numpy())
        
        if probabilities is not None:
            self.all_probabilities.extend(probabilities.cpu().numpy())
    
    def compute(self) -> Dict[str, float]:
        """
        Compute all metrics.
        
        Returns:
            Dictionary of metric names and values
        """
        preds = np.array(self.all_predictions)
        targets = np.array(self.all_targets)
        
        metrics = {}
        
        # Overall accuracy
        metrics['accuracy'] = accuracy_score(targets, preds)
        
        # Per-class metrics (precision, recall, f1)
        precision, recall, f1, support = precision_recall_fscore_support(
            targets, preds, average=None, zero_division=0
        )
        
        # Store per-class metrics
        for i in range(self.num_classes):
            class_name = self.class_names.get(i, f"class_{i}")
            metrics[f'{class_name}_precision'] = precision[i]
            metrics[f'{class_name}_recall'] = recall[i]  # = Sensitivity
            metrics[f'{class_name}_f1'] = f1[i]
        
        # Macro averages (equal weight to each class)
        metrics['macro_precision'] = precision.mean()
        metrics['macro_recall'] = recall.mean()
        metrics['macro_f1'] = f1.mean()
        
        # Weighted averages (weight by class frequency)
        precision_w, recall_w, f1_w, _ = precision_recall_fscore_support(
            targets, preds, average='weighted', zero_division=0
        )
        metrics['weighted_precision'] = precision_w
        metrics['weighted_recall'] = recall_w
        metrics['weighted_f1'] = f1_w
        
        # Melanoma-specific sensitivity (CRITICAL METRIC)
        melanoma_idx = 4  # mel = class 4
        metrics['melanoma_sensitivity'] = recall[melanoma_idx]
        
        # Specificity (per class)
        cm = confusion_matrix(targets, preds, labels=range(self.num_classes))
        for i in range(self.num_classes):
            # Specificity = TN / (TN + FP)
            tn = cm.sum() - (cm[i, :].sum() + cm[:, i].sum() - cm[i, i])
            fp = cm[:, i].sum() - cm[i, i]
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
            
            class_name = self.class_names.get(i, f"class_{i}")
            metrics[f'{class_name}_specificity'] = specificity
        
        # AUC-ROC (if probabilities available)
        if len(self.all_probabilities) > 0:
            probs = np.array(self.all_probabilities)
            
            try:
                # One-vs-rest AUC for each class
                auc_scores = []
                for i in range(self.num_classes):
                    # Binary labels: 1 if class i, 0 otherwise
                    binary_targets = (targets == i).astype(int)
                    class_probs = probs[:, i]
                    
                    # Only compute if we have both classes
                    if len(np.unique(binary_targets)) > 1:
                        auc = roc_auc_score(binary_targets, class_probs)
                        auc_scores.append(auc)
                        
                        class_name = self.class_names.get(i, f"class_{i}")
                        metrics[f'{class_name}_auc'] = auc
                
                # Macro AUC (average across classes)
                if auc_scores:
                    metrics['macro_auc'] = np.mean(auc_scores)
                
                # Multiclass AUC (weighted by support)
                metrics['weighted_auc'] = roc_auc_score(
                    targets, probs, multi_class='ovr', average='weighted'
                )
            except Exception as e:
                print(f"⚠️  Could not compute AUC: {e}")
        
        return metrics
    
    def get_confusion_matrix(self) -> np.ndarray:
        """
        Get confusion matrix.
        
        Returns:
            Confusion matrix [num_classes, num_classes]
        """
        preds = np.array(self.all_predictions)
        targets = np.array(self.all_targets)
        
        return confusion_matrix(targets, preds, labels=range(self.num_classes))
    
    def print_summary(self):
        """Print a formatted metrics summary."""
        metrics = self.compute()
        
        print("\n" + "="*60)
        print("📊 METRICS SUMMARY")
        print("="*60)
        
        print(f"\n🎯 Overall Performance:")
        print(f"   Accuracy:          {metrics['accuracy']:.4f}")
        print(f"   Macro F1:          {metrics['macro_f1']:.4f}")
        print(f"   Weighted F1:       {metrics['weighted_f1']:.4f}")
        
        if 'macro_auc' in metrics:
            print(f"   Macro AUC:         {metrics['macro_auc']:.4f}")
            print(f"   Weighted AUC:      {metrics['weighted_auc']:.4f}")
        
        print(f"\n🎯 CRITICAL: Melanoma Detection:")
        print(f"   Sensitivity (Recall): {metrics['melanoma_sensitivity']:.4f}")
        print(f"   → This is our most important metric!")
        
        print(f"\n📋 Per-Class Performance:")
        for i in range(self.num_classes):
            class_name = self.class_names.get(i, f"class_{i}")
            precision = metrics[f'{class_name}_precision']
            recall = metrics[f'{class_name}_recall']
            f1 = metrics[f'{class_name}_f1']
            
            print(f"   {class_name:6s}: P={precision:.3f} R={recall:.3f} F1={f1:.3f}")
        
        print("="*60)