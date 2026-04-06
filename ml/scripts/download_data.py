"""
DermaVision — Automated Dataset Download.

Downloads and organizes the HAM10000 dataset from Kaggle.

Requirements:
    - Kaggle API credentials in ~/.kaggle/kaggle.json
    - kaggle package: pip install kaggle
"""

import os
import zipfile
import shutil
from pathlib import Path
import subprocess

import pandas as pd
from sklearn.model_selection import train_test_split


def download_ham10000():
    """Download HAM10000 dataset from Kaggle."""
    
    # Define paths...
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"
    
    # Create directories
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    print("Downloading HAM10000 dataset from Kaggle...")
    print("This may take 5-10 minutes depending on your connection.\n")
    
    # Kaggle dataset identifier..
    dataset = "kmader/skin-cancer-mnist-ham10000"
    
    try:
        # Check if already downloaded
        zip_path = raw_dir / "skin-cancer-mnist-ham10000.zip"
        if not zip_path.exists() and not list(raw_dir.glob("*.jpg")):
            # Download using Kaggle API
            import sys
            kaggle_path = os.path.join(os.path.dirname(sys.executable), "kaggle")
            
            subprocess.run(
                [kaggle_path, "datasets", "download", "-d", dataset, "-p", str(raw_dir)],
                check=True
            )
            print("Download complete!\n")
        else:
            print("Dataset archive already exists or is extracted.\n")
        
        # Unzip the dataset entirely to processed dir
        if list(processed_dir.glob("*.jpg")):
             print(" Extracted images already exist in processed dir.\n")
        elif zip_path.exists():
            print("📂 Extracting files to processed directory...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(processed_dir)
            print("Extraction complete!\n")
        
        # Process metadata
        metadata_files = list(processed_dir.glob("*metadata*")) + list(raw_dir.glob("*metadata*"))
        if metadata_files:
            print("Processing metadata splits...")
            df = pd.read_csv(metadata_files[0])
            
            # Add train/val/test splits (80/10/10)
            train_df, temp_df = train_test_split(
                df, test_size=0.2, stratify=df["dx"], random_state=42
            )
            val_df, test_df = train_test_split(
                temp_df, test_size=0.5, stratify=temp_df["dx"], random_state=42
            )
            
            train_df["split"] = "train"
            val_df["split"] = "val"
            test_df["split"] = "test"
            
            final_df = pd.concat([train_df, val_df, test_df]).reset_index(drop=True)
            final_df.to_csv(data_dir / "metadata.csv", index=False)
            
            print(f"\n📊 Dataset splits saved to {data_dir / 'metadata.csv'}:")
            print(f"   Train: {len(train_df):,} images")
            print(f"   Val:   {len(val_df):,} images")
            print(f"   Test:  {len(test_df):,} images")
        
        return True
        
    except subprocess.CalledProcessError:
        print("❌ Error: Kaggle API not configured or dataset download failed.")
        print("\n🔧 To fix this:")
        print("1. Install Kaggle API: pip install kaggle")
        print("2. Get API credentials from https://www.kaggle.com/settings")
        print("3. Place kaggle.json in ~/.kaggle/")
        print("4. Run: chmod 600 ~/.kaggle/kaggle.json")
        return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = download_ham10000()
    
    if success:
        print("\n🎉 Dataset ready for training!")
    else:
        print("\n⚠️  Manual download needed. Visit:")
        print("   https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000")
