#!/bin/bash
# =============================================================
# DermaVision — Colab Training Launcher
#
# This script sets the correct working directory and launches
# the existing training pipeline. It does NOT modify any
# project code — it only ensures paths resolve correctly
# when running inside Google Colab.
#
# Usage (from Colab):
#   bash scripts/train_colab.sh
# =============================================================

set -e

# Resolve project root (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "============================================================"
echo "🚀 DermaVision — Colab Training Launcher"
echo "============================================================"
echo "  Project root : $PROJECT_ROOT"
echo "  Python       : $(python --version 2>&1)"
echo ""

# --- GPU check ---
echo "🖥️  GPU Information:"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
else
    echo "  ⚠️  No NVIDIA GPU detected (nvidia-smi not found)"
fi
echo ""

# --- Verify data exists ---
echo "📂 Verifying dataset..."
METADATA="$PROJECT_ROOT/data/metadata.csv"
if [ ! -f "$METADATA" ]; then
    echo "  ❌ metadata.csv not found at $METADATA"
    echo "     Run the Kaggle download cell first!"
    exit 1
fi
TRAIN_COUNT=$(grep -c ',train$' "$METADATA" || true)
VAL_COUNT=$(grep -c ',val$' "$METADATA" || true)
TEST_COUNT=$(grep -c ',test$' "$METADATA" || true)
echo "  Train : $TRAIN_COUNT samples"
echo "  Val   : $VAL_COUNT samples"
echo "  Test  : $TEST_COUNT samples"
echo ""

# --- Launch training ---
echo "🏋️  Launching training..."
echo "============================================================"

cd "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

python scripts/train.py
