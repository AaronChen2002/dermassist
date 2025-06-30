from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from PIL import Image
import io
import logging
import os
import torch

from .explainability import generate_request_id, generate_grad_cam_overlay
from .security import get_api_key, API_KEY_NAME, get_api_key_for_rate_limiting
from .config import settings
from .ml_utils import get_model, preprocess_image

# --- App Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Rate Limiting Setup ---
# Read Redis URL from environment variable, with a fallback for local dev without Docker
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
limiter = Limiter(key_func=get_api_key_for_rate_limiting, storage_uri=redis_url)

app = FastAPI(
    title="DermAssist API",
    description="API for classifying skin lesions and providing explainability.",
    version="1.0.0"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS Configuration ---
# Allow all origins for now, can be restricted in production
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Class Labels (from HAM10000) ---
CLASS_LABELS = {
    0: 'Actinic keratoses',
    1: 'Basal cell carcinoma',
    2: 'Benign keratosis-like lesions',
    3: 'Dermatofibroma',
    4: 'Melanoma',
    5: 'Melanocytic nevi',
    6: 'Vascular lesions'
}

@app.on_event("startup")
async def startup_event():
    """Actions to perform on application startup."""
    logging.info("Application startup...")
    # Load the machine learning model
    app.state.model = get_model()
    logging.info("ML model loaded.")
    logging.info("Application ready.")


@app.get("/")
def read_root():
    """Root endpoint to check API status."""
    return {"status": "DermAssist API is running."}


@app.post("/classify-lesion")
@limiter.limit("100/day")
async def classify_lesion(
    request: Request,
    file: UploadFile = File(...), 
    api_key: str = Depends(get_api_key)
):
    """
    Endpoint to classify a skin lesion from an uploaded image.
    Generates a heatmap and returns classification details.
    Requires API key authentication.
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File provided is not an image.")

    # Generate a unique ID for this request
    request_id = generate_request_id()

    # Read and preprocess the image
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    image_tensor = preprocess_image(contents)
    
    # Run inference
    with torch.no_grad():
        outputs = app.state.model(image_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted_class_idx = torch.max(probabilities, 1)

    predicted_label = CLASS_LABELS[predicted_class_idx.item()]
    confidence_score = confidence.item()

    # Generate Grad-CAM heatmap
    generate_grad_cam_overlay(
        model=app.state.model, 
        image=image, 
        image_tensor=image_tensor, 
        pred_class_idx=predicted_class_idx.item(),
        request_id=request_id
    )
    
    return {
        "label": predicted_label,
        "confidence": round(confidence_score, 4),
        "recommendation": f"Consultation recommended for '{predicted_label}'.", # Placeholder
        "request_id": request_id
    }


@app.get("/heatmap/{request_id}")
def get_heatmap(request_id: str):
    """
    Retrieves the Grad-CAM heatmap overlay image for a given request ID.
    """
    heatmap_path = os.path.join("heatmaps", f"{request_id}.png")
    if not os.path.exists(heatmap_path):
        raise HTTPException(status_code=404, detail="Heatmap not found for the given request ID.")
    
    return FileResponse(heatmap_path, media_type="image/png")
