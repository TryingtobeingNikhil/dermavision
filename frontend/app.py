"""
Streamlit UI for DermaVision

Simple, clean interface for skin lesion classification.
"""

import streamlit as st
import requests
from PIL import Image
import io
import base64
import numpy as np

# Page config
st.set_page_config(
    page_title="DermaVision - Skin Lesion Classifier",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API endpoint
API_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subheader {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .prediction-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .certain {
        background-color: #d4edda;
        border: 2px solid #28a745;
    }
    .uncertain {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
    }
    .warning {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🔬 DermaVision</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">AI-Powered Skin Lesion Classification with Clinical-Grade Uncertainty Detection</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.write("""
    DermaVision uses deep learning to classify skin lesions into 7 categories:
    
    - Melanoma (malignant)
    - Basal Cell Carcinoma (malignant)
    - Melanocytic Nevi (benign moles)
    - Benign Keratosis
    - Actinic Keratoses
    - Vascular Lesions
    - Dermatofibroma
    
    **Uncertainty Detection:**
    If the model's confidence is below 60%, it will recommend dermatologist review.
    """)
    
    st.divider()
    
    st.header("⚠️ Medical Disclaimer")
    st.warning("""
    This tool is for **educational purposes only**.
    
    ❌ NOT a substitute for professional medical diagnosis
    
    ✅ Always consult a dermatologist for medical concerns
    """)
    
    st.divider()
    
    # Model info
    try:
        response = requests.get(f"{API_URL}/model-info", timeout=2)
        if response.status_code == 200:
            info = response.json()
            st.success(f"✅ Model: {info['model_name']}")
            st.info(f"🎯 Threshold: {info['uncertainty_threshold']:.0%}")
    except:
        st.error("⚠️ API not reachable")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 Upload Image")
    
    uploaded_file = st.file_uploader(
        "Choose a dermoscopic image",
        type=['jpg', 'jpeg', 'png'],
        help="Upload a clear image of the skin lesion"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        
        # Analyze button
        if st.button("🔍 Analyze Lesion", type="primary", use_container_width=True):
            with st.spinner("Analyzing image..."):
                try:
                    # Call API
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'image/jpeg')}
                    response = requests.post(
                        f"{API_URL}/predict",
                        files=files,
                        params={'include_gradcam': True},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Store in session state
                        st.session_state['result'] = result
                        st.rerun()
                    else:
                        st.error(f"API Error: {response.status_code}")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("Make sure the API is running: `uvicorn api.main:app --port 8000`")

with col2:
    st.header("📊 Results")
    
    if 'result' in st.session_state:
        result = st.session_state['result']
        
        # Prediction box
        if result['uncertain']:
            st.markdown(f"""
            <div class="prediction-box uncertain">
                <h3>⚠️ UNCERTAIN - Dermatologist Review Recommended</h3>
                <p style="font-size: 1.1rem;">
                    <strong>Top Prediction:</strong> {result['predicted_class_code'].upper()}<br>
                    <strong>Confidence:</strong> {result['confidence']:.1%}
                </p>
                <p>{result['message']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="prediction-box certain">
                <h3>✅ Prediction: {result['prediction']}</h3>
                <p style="font-size: 1.1rem;">
                    <strong>Confidence:</strong> {result['confidence']:.1%}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # All probabilities
        st.subheader("📈 All Class Probabilities")
        
        if 'all_probabilities' in result:
            probs = result['all_probabilities']
            
            # Create bar chart
            for class_name, prob in probs.items():
                # Highlight top prediction
                if class_name == result.get('prediction') or \
                   (result['uncertain'] and class_name == result['all_probabilities'][list(probs.keys())[0]]):
                    color = "#ffc107" if result['uncertain'] else "#28a745"
                else:
                    color = "#007bff"
                
                st.markdown(f"""
                <div style="margin: 0.5rem 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.2rem;">
                        <span>{class_name}</span>
                        <span><strong>{prob:.1%}</strong></span>
                    </div>
                    <div style="background-color: #e0e0e0; border-radius: 5px; height: 25px;">
                        <div style="background-color: {color}; width: {prob*100}%; height: 100%; border-radius: 5px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Grad-CAM visualization
        if 'gradcam_base64' in result:
            st.subheader("🔥 Grad-CAM Heatmap")
            st.info("Highlights which regions influenced the model's decision")
            
            # Decode base64 image
            gradcam_bytes = base64.b64decode(result['gradcam_base64'])
            gradcam_image = Image.open(io.BytesIO(gradcam_bytes))
            
            st.image(gradcam_image, caption="Model Attention Map", use_container_width=True)
    
    else:
        st.info("👆 Upload an image to get started")
        
        # Example
        st.markdown("""
        ### How it works:
        
        1. **Upload** a dermoscopic image
        2. **AI analyzes** the lesion features
        3. **Get prediction** with confidence score
        4. **View heatmap** showing what the model focused on
        5. **Uncertainty warning** if confidence < 60%
        """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>DermaVision v1.0 | Built with PyTorch, FastAPI, and Streamlit</p>
    <p style="font-size: 0.9rem;">⚕️ For educational purposes only - Not FDA approved</p>
</div>
""", unsafe_allow_html=True)