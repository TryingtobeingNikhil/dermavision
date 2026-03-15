"""
DermaVision — UI Helper Functions.

Utility functions for the Streamlit interface.
"""

import io
import base64

import numpy as np
from PIL import Image


def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


def resize_image(image: Image.Image, max_size: int = 600) -> Image.Image:
    """Resize image maintaining aspect ratio."""
    ratio = min(max_size / image.width, max_size / image.height)
    if ratio < 1:
        new_size = (int(image.width * ratio), int(image.height * ratio))
        image = image.resize(new_size, Image.LANCZOS)
    return image


def format_confidence(confidence: float) -> str:
    """Format confidence value with color-coded label."""
    if confidence >= 0.9:
        return f"🟢 High ({confidence:.1%})"
    elif confidence >= 0.7:
        return f"🟡 Moderate ({confidence:.1%})"
    else:
        return f"🔴 Low ({confidence:.1%})"


def get_severity_badge(severity: str) -> str:
    """Return styled severity badge."""
    badges = {
        "low": "🟢 Low Risk",
        "high": "🟡 High Risk",
        "critical": "🔴 Critical",
    }
    return badges.get(severity, "⚪ Unknown")
