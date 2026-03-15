"""
DermaVision — Evaluation Script.

Comprehensive model evaluation with metrics reporting and visualization.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import torch
from tqdm import tqdm

from src.data.dataloader import create_dataloaders
from src.models.cnn_model import DermaModel
from src.models.metrics import compute_metrics, sensitivity_at_specificity
from src.training.utils import load_config, get_device
from src.visualization.plots import plot_confusion_matrix, plot_training_curves


def main():
    parser = argparse.ArgumentParser(description="DermaVision Evaluation")
    parser.add_argument("--config", type=str, default="config/config.yaml")
    parser.add_argument("--model_path", type=str, default="models/best_model.pth")
    parser.add_argument("--split", type=str, default="test", choices=["val", "test"])
    parser.add_argument("--device", type=str, default="auto")
    parser.add_argument("--output_dir", type=str, default="results")
    args = parser.parse_args()

    config = load_config(args.config)
    device = get_device(args.device)

    print("\n🔬 DermaVision Evaluation")
    print("=" * 60)

    # Load data
    dataloaders = create_dataloaders(
        metadata_path=config["data"]["metadata_path"],
        image_dir=config["data"]["processed_dir"],
        batch_size=config["training"]["batch_size"],
        image_size=config["data"]["image_size"],
    )
    loader = dataloaders[args.split]
    print(f"📊 Evaluating on {args.split} set: {len(loader.dataset):,} samples")

    # Load model
    checkpoint = torch.load(args.model_path, map_location=device)
    model = DermaModel(num_classes=config["model"]["num_classes"], pretrained=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    print(f"✅ Model loaded from {args.model_path}")

    # Inference
    all_preds, all_labels, all_probs = [], [], []

    with torch.no_grad():
        for images, labels in tqdm(loader, desc="Evaluating"):
            images = images.to(device)
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1)
            preds = probs.argmax(dim=1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())
            all_probs.extend(probs.cpu().numpy())

    y_true = np.array(all_labels)
    y_pred = np.array(all_preds)
    y_prob = np.array(all_probs)

    # Compute metrics
    class_names = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]
    metrics = compute_metrics(y_true, y_pred, y_prob, class_names)

    # Melanoma sensitivity at 95% specificity
    mel_sens = sensitivity_at_specificity(y_true, y_prob, target_specificity=0.95, class_idx=4)

    # Print results
    print(f"\n{'='*60}")
    print(f"📊 Results on {args.split} set:")
    print(f"{'='*60}")
    print(f"  Accuracy:           {metrics['accuracy']:.4f}")
    print(f"  Balanced Accuracy:  {metrics['balanced_accuracy']:.4f}")
    print(f"  Weighted F1:        {metrics['weighted_f1']:.4f}")
    print(f"  Macro F1:           {metrics['macro_f1']:.4f}")
    print(f"  Cohen's Kappa:      {metrics['cohen_kappa']:.4f}")
    if metrics.get("auc_roc_macro"):
        print(f"  AUC-ROC (macro):    {metrics['auc_roc_macro']:.4f}")
    print(f"  Melanoma Sensitivity @95% Specificity: {mel_sens:.4f}")

    print(f"\n📋 Per-class Performance:")
    for name, stats in metrics["per_class"].items():
        print(f"  {name:6s}  Sens: {stats['sensitivity']:.4f}  "
              f"Spec: {stats['specificity']:.4f}  Support: {stats['support']}")

    # Save results
    os.makedirs(args.output_dir, exist_ok=True)

    # Save metrics JSON
    save_metrics = {k: v for k, v in metrics.items() if k != "classification_report"}
    with open(os.path.join(args.output_dir, "metrics.json"), "w") as f:
        json.dump(save_metrics, f, indent=2, default=str)

    # Save confusion matrix plot
    plot_confusion_matrix(
        y_true, y_pred, class_names,
        save_path=os.path.join(args.output_dir, "confusion_matrix.png"),
    )

    print(f"\n✅ Results saved to {args.output_dir}/")


if __name__ == "__main__":
    main()
