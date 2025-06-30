import os
import uuid
from PIL import Image, ImageDraw
import logging

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constants ---
HEATMAP_DIR = "heatmaps"
os.makedirs(HEATMAP_DIR, exist_ok=True)


def generate_grad_cam_overlay(image: Image.Image, request_id: str):
    """
    Generates and saves a Grad-CAM heatmap overlay for a given image.

    This is currently a placeholder function that creates a dummy
    heatmap. It will be replaced with a proper Grad-CAM implementation
    once the model is integrated.
    """
    logging.info(f"Generating dummy heatmap for request_id: {request_id}")

    # Create a dummy red overlay as a placeholder for the real heatmap
    overlay = Image.new('RGBA', image.size, (255, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Draw a semi-transparent red rectangle to simulate a heatmap
    # In a real scenario, this would be a pixel-wise overlay based on model gradients
    draw.rectangle(
        (image.width * 0.2, image.height * 0.2, image.width * 0.8, image.height * 0.8),
        fill=(255, 0, 0, 128)
    )

    # Blend the original image with the overlay
    blended_image = Image.alpha_composite(image.convert('RGBA'), overlay)
    
    heatmap_path = os.path.join(HEATMAP_DIR, f"{request_id}.png")
    blended_image.convert('RGB').save(heatmap_path)
    
    logging.info(f"Dummy heatmap saved to {heatmap_path}")
    return heatmap_path

def generate_request_id() -> str:
    """Generates a unique request ID."""
    return str(uuid.uuid4())
