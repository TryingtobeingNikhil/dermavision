# 🔬 DermaVision — AI-Powered Skin Lesion Classification

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/PyTorch-2.0+-red.svg" alt="PyTorch">
  <img src="https://img.shields.io/badge/FastAPI-0.100+-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

> A deep learning pipeline for automated classification of dermatological conditions from clinical images, built on the HAM10000 dataset using EfficientNet-B3 with Grad-CAM explainability.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Training](#training)
- [Inference & API](#inference--api)
- [Results](#results)
- [Contributing](#contributing)
- [License](#license)

---

## 🧠 Overview

DermaVision leverages a fine-tuned **EfficientNet-B3** model to classify skin lesions into 7 diagnostic categories from the HAM10000 dataset. The project addresses class imbalance through **Focal Loss**, provides visual explanations via **Grad-CAM**, and includes confidence calibration for clinical-grade predictions.

### Supported Diagnostic Categories

| Abbreviation | Condition |
|-------------|-----------|
| **akiec** | Actinic Keratoses / Intraepithelial Carcinoma |
| **bcc** | Basal Cell Carcinoma |
| **bkl** | Benign Keratosis |
| **df** | Dermatofibroma |
| **mel** | Melanoma |
| **nv** | Melanocytic Nevi |
| **vasc** | Vascular Lesions |

---

## ✨ Key Features

- **EfficientNet-B3 Backbone** — State-of-the-art transfer learning with ImageNet pretrained weights
- **Focal Loss** — Handles severe class imbalance (nv vs. df ratio ~57:1)
- **Albumentations Pipeline** — Advanced augmentation with geometric + color transforms
- **Grad-CAM Explainability** — Visual attention maps for model interpretability
- **Confidence Calibration** — Temperature scaling for clinical-grade uncertainty estimation
- **FastAPI Deployment** — Production-ready REST API with health monitoring
- **Streamlit UI** — Interactive web interface for real-time predictions
- **TensorBoard Logging** — Comprehensive training monitoring
- **ONNX Export** — Optimized model export for edge deployment
- **Docker Support** — Containerized deployment with multi-stage builds

---

## 📁 Project Structure

```
dermavision/
├── config/                 # Configuration files
├── data/                   # Dataset (raw, processed, metadata)
├── notebooks/              # Jupyter notebooks for EDA & analysis
├── src/                    # Source code
│   ├── data/               # Dataset & augmentation pipeline
│   ├── models/             # Model architecture, loss, metrics
│   ├── training/           # Training loop & callbacks
│   ├── inference/          # Prediction & uncertainty
│   └── visualization/      # Grad-CAM & plotting
├── api/                    # FastAPI REST API
├── ui/                     # Streamlit web interface
├── models/                 # Saved model weights
├── logs/                   # Training logs & TensorBoard
├── tests/                  # Unit tests
└── scripts/                # Utility scripts
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- CUDA 11.8+ (for GPU training)
- Docker (optional, for containerized deployment)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/dermavision.git
cd dermavision

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Dataset Setup

```bash
# Download HAM10000 dataset
python scripts/download_data.py

# Verify data integrity
python -m pytest tests/test_data.py -v
```

---

## 🏋️ Training

```bash
# Start training with default config
python scripts/train.py

# Monitor with TensorBoard
tensorboard --logdir logs/tensorboard

# Custom training
python scripts/train.py --config config/config.yaml --epochs 50 --batch_size 32
```

---

## 🔮 Inference & API

### FastAPI Server

```bash
# Start the API server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Health check
curl http://localhost:8000/health

# Predict
curl -X POST http://localhost:8000/predict \
  -F "file=@path/to/skin_image.jpg"
```

### Streamlit UI

```bash
streamlit run ui/app.py
```

### Docker Deployment

```bash
docker build -t dermavision .
docker run -p 8000:8000 dermavision
```

---

## 📊 Results

| Metric | Value |
|--------|-------|
| Accuracy | TBD |
| Weighted F1 | TBD |
| Melanoma Sensitivity | TBD |
| AUC-ROC (macro) | TBD |

> Results will be populated after training on the full HAM10000 dataset.

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [HAM10000 Dataset](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T) — Tschandl et al.
- [EfficientNet](https://arxiv.org/abs/1905.11946) — Tan & Le, 2019
- [Focal Loss](https://arxiv.org/abs/1708.02002) — Lin et al., 2017
