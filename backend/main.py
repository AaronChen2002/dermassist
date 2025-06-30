from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image
import io
import logging
import os

from .explainability import generate_request_id, generate_grad_cam_overlay
from .security import get_api_key

# --- App Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="DermAssist API",
    description="API for classifying skin lesions and providing explainability.",
    version="1.0.0"
)

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


@app.on_event("startup")
async def startup_event():
    """Actions to perform on application startup."""
    logging.info("Application startup...")
    # In a future step, we will load the model here
    # app.state.model = load_model()
    logging.info("Application ready.")


@app.get("/")
def read_root():
    """Root endpoint to check API status."""
    return {"status": "DermAssist API is running."}


@app.post("/classify-lesion")
async def classify_lesion(
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

    # Read image
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    # --- Placeholder Logic ---
    # In future steps, we will run actual model inference here.
    # For now, we use dummy data and generate a dummy heatmap.
    
    # Generate and save a (dummy) heatmap overlay
    generate_grad_cam_overlay(image, request_id)
    
    # Placeholder response
    return {
        "label": "melanoma",
        "confidence": 0.85,
        "recommendation": "Urgent dermatologist consultation recommended.",
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
