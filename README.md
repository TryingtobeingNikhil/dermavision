# 🔬 DermaVision — AI-Powered Skin Lesion Classification

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/PyTorch-2.x-red.svg" alt="PyTorch">
  <img src="https://img.shields.io/badge/FastAPI-0.1x-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/Next.js-14-black.svg" alt="Next.js">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

> A full-stack monorepo for automated classification of dermatological conditions from clinical images, built on the HAM10000 dataset using EfficientNet-B3, with Grad-CAM explainability and a modern Next.js frontend.

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

Monorepo layout:

```
dermavision/
├── frontend/               # Next.js 14 UI (TypeScript + Tailwind)
│   ├── app/                # App router pages & layout
│   ├── components/         # Hero, scanner, results, dashboard, effects
│   ├── lib/                # Frontend utilities (API helpers, animations)
│   └── public/             # Static assets
├── backend/                # FastAPI inference server
│   ├── app/
│   │   ├── main.py         # FastAPI app, /health, /model-info, /predict
│   │   ├── endpoints/      # Modular endpoints
│   │   └── schemas.py      # Pydantic schemas
│   └── run.py              # Uvicorn entrypoint
├── ml/                     # ML training & core inference code
│   ├── config/             # YAML / JSON config
│   ├── src/
│   │   ├── data/           # Dataset & augmentations (HAM10000)
│   │   ├── models/         # CNN model, loss functions, metrics
│   │   ├── training/       # Trainer, callbacks, utilities
│   │   ├── inference/      # Predictor, uncertainty
│   │   └── visualization/  # Grad-CAM & plotting
│   ├── scripts/            # train, evaluate, export_onnx, etc.
│   ├── notebooks/          # EDA & results analysis
│   ├── models/             # Saved model weights (e.g. best_model.pth)
│   └── logs/               # Training logs & TensorBoard
├── data/                   # Dataset (raw, processed, metadata.csv)
├── tests/                  # Python test suite (data, model, pipeline, API)
├── requirements.txt        # Python dependencies
└── Dockerfile              # Containerization (API)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- CUDA 11.8+ (for GPU training)
- Docker (optional, for containerized deployment)

### Installation (backend + ML)

```bash
# Clone the repository
git clone https://github.com/yourusername/dermavision.git
cd dermavision

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install Python dependencies
pip install -r requirements.txt
```

### Frontend (Next.js) setup

```bash
cd frontend
npm install
```

### Dataset Setup

```bash
# From repo root
source venv/bin/activate

# Download & preprocess HAM10000 dataset
python ml/scripts/download_data.py

# Verify data integrity
pytest tests/test_data.py -v
```

---

## 🏋️ Training

```bash
source venv/bin/activate

# Start training with default hyperparameters
python ml/scripts/train.py

# Monitor with TensorBoard
tensorboard --logdir ml/logs/tensorboard

# Example: custom config / options (if you wire CLI flags)
# python ml/scripts/train.py --config ml/config/config.yaml --epochs 50 --batch_size 32
```

---

## 🔮 Inference, API & Frontend

### FastAPI backend

From the repo root:

```bash
source venv/bin/activate
python backend/run.py
```

This starts the API on `http://localhost:8000`.

- **Swagger docs**: `http://localhost:8000/docs`
- **Health check**:

  ```bash
  curl http://localhost:8000/health
  ```

- **Model info**:

  ```bash
  curl http://localhost:8000/model-info
  ```

- **Single-image prediction**:

  ```bash
  curl -X POST "http://localhost:8000/predict?include_gradcam=true" \
    -F "file=@path/to/skin_image.jpg"
  ```

The `/predict` response includes the predicted class, confidence, uncertainty flag, and an optional Grad-CAM overlay encoded as base64.

### Next.js frontend (primary UI)

From the repo root:

```bash
cd frontend
npm run dev
```

- App URL: `http://localhost:3000`
- The frontend:
  - Lets you upload a dermoscopic image
  - Sends it to the backend `/predict` endpoint
  - Renders prediction, confidence, class probabilities, and Grad-CAM heatmap

By default, the frontend points to the local backend:

- `NEXT_PUBLIC_API_BASE_URL` (optional): if absent, it falls back to `http://localhost:8000`.

### Docker Deployment

```bash
docker build -t dermavision .
docker run -p 8000:8000 dermavision
```

---

## 📊 Results

| Metric                 | Value  |
|------------------------|--------|
| Train Accuracy         | 0.8558 |
| Train F1 (weighted)    | 0.8492 |
| Val Accuracy           | 0.6214 |
| Val F1 (weighted)      | 0.6803 |
| Best Val F1            | 0.7155 |
| Melanoma Sensitivity   | 0.8739 |

> These metrics are from the current best checkpoint (`ml/models/best_model.pth`) trained on HAM10000; you can update them after future training runs.

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
