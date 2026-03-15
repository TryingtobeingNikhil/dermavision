"""
DermaVision — Streamlit Web Interface.

Interactive UI for uploading skin lesion images and viewing
classification results with Grad-CAM explanations.
"""

import io
import json
import tempfile

import numpy as np
import streamlit as st
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="DermaVision — Skin Lesion Classifier",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_class_info():
    """Load class mapping for display."""
    try:
        with open("config/class_mapping.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def main():
    """Main Streamlit application."""

    # Header
    st.title("🔬 DermaVision")
    st.markdown("### AI-Powered Skin Lesion Classification")
    st.markdown(
        "Upload a dermatoscopic image to get an AI-powered diagnostic prediction "
        "with confidence scores and visual explanations."
    )
    st.divider()

    # Sidebar
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown(
            "DermaVision uses an **EfficientNet-B3** model trained on the "
            "HAM10000 dataset to classify skin lesions into 7 categories."
        )

        st.divider()

        st.header("📋 Supported Classes")
        class_info = load_class_info()
        if class_info:
            for idx, info in class_info["classes"].items():
                severity_emoji = {"low": "🟢", "high": "🟡", "critical": "🔴"}
                emoji = severity_emoji.get(info["severity"], "⚪")
                st.markdown(f"{emoji} **{info['abbreviation'].upper()}** — {info['name']}")

        st.divider()
        st.markdown("⚠️ **Disclaimer**: This tool is for research purposes only. "
                    "Always consult a dermatologist for medical advice.")

    # Main content
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📤 Upload Image")
        uploaded_file = st.file_uploader(
            "Choose a dermatoscopic image",
            type=["jpg", "jpeg", "png"],
            help="Upload a JPEG or PNG image of a skin lesion.",
        )

        if uploaded_file is not None:
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="Uploaded Image", use_container_width=True)

            if st.button("🔍 Analyze", type="primary", use_container_width=True):
                with st.spinner("Analyzing image..."):
                    try:
                        # Save temp image
                        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                            image.save(tmp.name)

                            # Run prediction
                            from src.inference.predictor import Predictor
                            predictor = Predictor()
                            result = predictor.predict(tmp.name)

                        # Display results
                        with col2:
                            st.subheader("📊 Results")
                            display_results(result)

                    except Exception as e:
                        st.error(f"Prediction failed: {str(e)}")
                        st.info("Ensure the model weights are available at `models/best_model.pth`.")

    if uploaded_file is None:
        with col2:
            st.subheader("📊 Results")
            st.info("Upload an image and click 'Analyze' to see results.")


def display_results(result: dict):
    """Display prediction results with uncertainty awareness."""

    # Uncertainty check (threshold: 0.60)
    if result.get("is_uncertain", False):
        st.warning(
            "⚠️ **UNCERTAIN** — Confidence below 60% threshold.\n\n"
            "This prediction may not be reliable. "
            "**Please seek evaluation from a qualified dermatologist.**"
        )
        st.divider()

    # Main prediction
    st.metric(
        label="Predicted Diagnosis",
        value=result["class_name"],
        delta=f"Confidence: {result['confidence']:.1%}",
    )

    if result["is_malignant"]:
        st.error("⚠️ **MALIGNANT** — Referral to dermatologist recommended.")
    else:
        st.success("✅ **BENIGN** — Low risk, but monitor for changes.")

    # Confidence status
    if result["confidence"] >= 0.60:
        st.info(f"🎯 {result.get('uncertainty_message', 'Prediction confident.')}")

    st.divider()

    # Probability distribution
    st.markdown("**Class Probabilities:**")
    for cls, prob in sorted(result["probabilities"].items(), key=lambda x: -x[1]):
        st.progress(prob, text=f"{cls.upper()}: {prob:.1%}")


if __name__ == "__main__":
    main()
