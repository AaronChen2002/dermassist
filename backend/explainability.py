import os
import uuid
from PIL import Image
import logging
import torch
from torchcam.methods import GradCAM
from torchcam.utils import overlay_mask
from torchvision.transforms.functional import to_pil_image, to_tensor

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constants ---
HEATMAP_DIR = "heatmaps"
os.makedirs(HEATMAP_DIR, exist_ok=True)


def generate_grad_cam_overlay(
    model: torch.nn.Module, 
    image: Image.Image, 
    image_tensor: torch.Tensor, 
    pred_class_idx: int,
    request_id: str
):
    """
    Generates and saves a Grad-CAM heatmap overlay for a given image and model prediction.
    """
    logging.info(f"Generating Grad-CAM heatmap for request_id: {request_id}")

    try:
        # Find the last convolutional layer of MobileNetV2 for Grad-CAM
        # The target layer is typically the 'features' block.
        target_layer = model.features
        
        # Create a Grad-CAM extractor
        with GradCAM(model, target_layer=target_layer) as cam_extractor:
            # Preprocess your data and feed it to the model
            scores = model(image_tensor)
            
            # Retrieve the CAM for the predicted class
            activation_map = cam_extractor(class_idx=pred_class_idx, scores=scores)[0]

        # Resize the CAM and overlay it
        result = overlay_mask(image, to_pil_image(activation_map.squeeze(0), mode='F'), alpha=0.5)

        heatmap_path = os.path.join(HEATMAP_DIR, f"{request_id}.png")
        result.save(heatmap_path)
        
        logging.info(f"Grad-CAM heatmap saved to {heatmap_path}")
        return heatmap_path

    except Exception as e:
        logging.error(f"Failed to generate Grad-CAM heatmap: {e}")
        # As a fallback, save the original image so the endpoint doesn't fail
        fallback_path = os.path.join(HEATMAP_DIR, f"{request_id}.png")
        image.save(fallback_path)
        logging.warning(f"Saved original image as fallback to {fallback_path}")
        return fallback_path


def generate_request_id() -> str:
    """Generates a unique request ID."""
    return str(uuid.uuid4())
