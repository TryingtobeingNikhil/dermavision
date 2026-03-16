"""
DermaVision — ONNX Model Export.

Export the trained PyTorch model to ONNX format for optimized
inference in production environments.
"""

import argparse
import os
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

import numpy as np
import torch

from ml.src.models.cnn_model import DermaModel
from ml.src.training.utils import load_config, count_parameters


def export_to_onnx(
    model_path: str = str(repo_root / "ml" / "models" / "best_model.pth"),
    output_path: str = str(repo_root / "ml" / "models" / "dermavision.onnx"),
    image_size: int = 300,
    num_classes: int = 7,
    opset_version: int = 17,
    verify: bool = True,
):
    """Export PyTorch model to ONNX format.

    Args:
        model_path: Path to trained model checkpoint.
        output_path: Path for exported ONNX model.
        image_size: Input image size.
        num_classes: Number of output classes.
        opset_version: ONNX opset version.
        verify: Whether to verify the exported model.
    """
    print("\nDermaVision ONNX Export")
    print("=" * 60)

    # Load model
    checkpoint = torch.load(model_path, map_location="cpu")
    model = DermaModel(num_classes=num_classes, pretrained=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    params = count_parameters(model)
    print(f"  Model params: {params['total']:,}")

    # Create dummy input
    dummy_input = torch.randn(1, 3, image_size, image_size)

    # Export
    print(f"  Exporting to {output_path}...")
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=opset_version,
        do_constant_folding=True,
        input_names=["image"],
        output_names=["logits"],
        dynamic_axes={
            "image": {0: "batch_size"},
            "logits": {0: "batch_size"},
        },
    )

    # File size
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  ONNX model size: {file_size:.1f} MB")

    # Verify
    if verify:
        print("  Verifying ONNX model...")
        import onnx
        import onnxruntime as ort

        onnx_model = onnx.load(output_path)
        onnx.checker.check_model(onnx_model)

        # Compare outputs
        session = ort.InferenceSession(output_path)
        onnx_output = session.run(
            None, {"image": dummy_input.numpy()}
        )[0]

        with torch.no_grad():
            pytorch_output = model(dummy_input).numpy()

        max_diff = np.max(np.abs(pytorch_output - onnx_output))
        print(f"  Max output difference: {max_diff:.6e}")
        assert max_diff < 1e-4, f"Output mismatch too large: {max_diff}"

        print("  ✅ Verification passed!")

    print(f"\n✅ Export complete: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="DermaVision ONNX Export")
    parser.add_argument("--model_path", type=str, default=str(repo_root / "ml" / "models" / "best_model.pth"))
    parser.add_argument("--output", type=str, default=str(repo_root / "ml" / "models" / "dermavision.onnx"))
    parser.add_argument("--image_size", type=int, default=300)
    parser.add_argument("--no_verify", action="store_true")
    args = parser.parse_args()

    export_to_onnx(
        model_path=args.model_path,
        output_path=args.output,
        image_size=args.image_size,
        verify=not args.no_verify,
    )


if __name__ == "__main__":
    main()
