import torch
from torchvision import transforms, models
from PIL import Image
import io
import logging

# --- Constants ---
MODEL_PATH = "models/dermassist_mobilenet_v2.pt"
NUM_CLASSES = 7  # From the HAM10000 dataset
IMAGE_SIZE = 224

# --- Model Loading ---
def get_model():
    """Loads the pretrained MobileNetV2 model and adapts it for our classification task."""
    logging.info("Initializing MobileNetV2 model...")
    model = models.mobilenet_v2() # We don't need pretrained weights, just the architecture
    
    # Adapt the classifier to our number of classes
    model.classifier[1] = torch.nn.Sequential(
        torch.nn.Linear(model.last_channel, 256),
        torch.nn.ReLU(),
        torch.nn.Dropout(0.5),
        torch.nn.Linear(256, NUM_CLASSES)
    )
    
    logging.info(f"Loading model weights from {MODEL_PATH}")
    # Load the state dictionary. We map to CPU for broader compatibility, 
    # but it will run on CUDA if available.
    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
    model.eval()  # Set the model to evaluation mode
    return model

# --- Image Preprocessing ---
def preprocess_image(image_bytes: bytes) -> torch.Tensor:
    """Takes image bytes, preprocesses it, and returns a tensor."""
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return transform(image).unsqueeze(0) 