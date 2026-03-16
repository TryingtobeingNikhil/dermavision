"""Test inference pipeline."""

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from ml.src.inference.predictor import SkinLesionPredictor


def test_predictor():
    """Test single image prediction."""
    
    print("🧪 Testing Inference Pipeline\n")
    
    # Initialize predictor
    predictor = SkinLesionPredictor(
        model_path=str(repo_root / 'ml' / 'models' / 'best_model.pth'),
        device='mps',  # or 'cpu'
        confidence_threshold=0.60
    )
    
    # Find a test image
    test_images_dir = Path('data/processed/HAM10000_images_part_1')
    test_image = list(test_images_dir.glob('*.jpg'))[0]
    
    print(f"\n🔍 Testing on image: {test_image.name}\n")
    
    # Make prediction
    result = predictor.predict(str(test_image))
    
    # Print results
    print("="*60)
    print("PREDICTION RESULT")
    print("="*60)
    print(f"Image: {test_image.name}")
    print(f"Prediction: {result['prediction']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Uncertain: {result['uncertain']}")
    print(f"Message: {result['message']}")
    
    if 'all_probabilities' in result:
        print(f"\nAll probabilities:")
        for class_name, prob in result['all_probabilities'].items():
            bar = '█' * int(prob * 50)
            print(f"  {class_name:25s} {prob:6.2%} {bar}")
    
    print("="*60)
    print("\n✅ Inference test passed!")


def test_gradcam():
    """Test Grad-CAM visualization."""
    
    print("\n🧪 Testing Grad-CAM Visualization\n")
    
    # Initialize predictor
    predictor = SkinLesionPredictor(
        model_path=str(repo_root / 'ml' / 'models' / 'best_model.pth'),
        device='mps',
        confidence_threshold=0.60
    )
    
    # Find test images
    test_images_dir = repo_root / 'data' / 'processed' / 'HAM10000_images_part_1'
    test_images = list(test_images_dir.glob('*.jpg'))[:3]  # Test on 3 images
    
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(3, 2, figsize=(12, 16))
    
    for i, test_image in enumerate(test_images):
        print(f"Processing {test_image.name}...")
        
        # Predict with Grad-CAM
        result = predictor.predict_with_gradcam(str(test_image))
        
        # Plot original
        axes[i, 0].imshow(result['original_image'])
        axes[i, 0].set_title(f'Original: {test_image.name}', fontsize=10)
        axes[i, 0].axis('off')
        
        # Plot Grad-CAM overlay
        axes[i, 1].imshow(result['gradcam_overlay'])
        
        title = f"Prediction: {result['prediction']}\n"
        title += f"Confidence: {result['confidence']:.1%}"
        if result['uncertain']:
            title += " ⚠️ UNCERTAIN"
        
        axes[i, 1].set_title(title, fontsize=10, fontweight='bold')
        axes[i, 1].axis('off')
    
    plt.tight_layout()
    plt.savefig(repo_root / 'ml' / 'logs' / 'gradcam_examples.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print("\n✅ Grad-CAM test passed!")
    print("📊 Visualization saved to logs/gradcam_examples.png")


if __name__ == '__main__':
    test_predictor()
    test_gradcam()