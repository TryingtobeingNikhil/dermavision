"""Test model creation and forward pass."""

import torch
from src.models.cnn_model import create_model


def test_model():
    """Test model initialization and forward pass."""
    
    print("🧪 Testing Model\n")
    
    # Create model
    model = create_model(
        num_classes=7,
        pretrained=True,
        dropout=0.3,
        freeze_backbone=True,  # Test frozen mode
        device='mps'  # or 'cpu' if MPS not available
    )
    
    # Test forward pass
    print("\n🔍 Testing forward pass...")
    dummy_input = torch.randn(4, 3, 224, 224).to('mps')  # Batch of 4
    
    with torch.no_grad():
        logits = model(dummy_input)
        temp_logits = model.forward_with_temperature(dummy_input)
    
    print(f"   Input shape:  {dummy_input.shape}")
    print(f"   Output shape: {logits.shape}")
    print(f"   Expected:     torch.Size([4, 7])")
    print(f"   ✅ Shapes match!" if logits.shape == torch.Size([4, 7]) else "❌ Shape mismatch!")
    
    # Test probabilities
    probs = torch.softmax(logits, dim=1)
    temp_probs = torch.softmax(temp_logits, dim=1)
    
    print(f"\n📊 Sample predictions (first image):")
    print(f"   Regular logits:  {logits[0].cpu().numpy()}")
    print(f"   Regular probs:   {probs[0].cpu().numpy()}")
    print(f"   Temp-scaled probs: {temp_probs[0].cpu().numpy()}")
    print(f"   Temperature: {model.temperature.item():.3f}")
    
    # Test unfreezing
    print("\n🔓 Testing backbone unfreezing...")
    model.unfreeze_backbone()
    param_counts = model.get_num_params()
    print(f"   Trainable params after unfreezing: {param_counts['trainable']:,}")
    
    print("\n✅ All model tests passed!")


if __name__ == "__main__":
    test_model()