"""UI utility functions."""

def format_confidence(confidence: float) -> str:
    """Format confidence percentage with color."""
    if confidence >= 0.80:
        return f"🟢 {confidence:.1%}"
    elif confidence >= 0.60:
        return f"🟡 {confidence:.1%}"
    else:
        return f"🔴 {confidence:.1%}"