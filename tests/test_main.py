from fastapi.testclient import TestClient
from backend.main import app
from backend.config import settings

# client = TestClient(app) # This is no longer needed globally

# Use the first key from the settings for testing
VALID_API_KEY = list(settings.API_KEYS)[0] if settings.API_KEYS else "default-key-for-testing"


def test_health_check():
    """
    Tests the /health endpoint.
    It should return a 200 OK status.
    """
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_classify_lesion_success():
    """
    Tests the /classify-lesion endpoint with a valid API key and image.
    It should return a 200 OK status and a valid prediction structure.
    """
    with TestClient(app) as client:
        with open("sample_lesion.jpg", "rb") as f:
            response = client.post(
                "/classify-lesion",
                headers={"X-API-Key": VALID_API_KEY},
                files={"file": ("sample_lesion.jpg", f, "image/jpeg")},
            )
        assert response.status_code == 200
        data = response.json()
        assert "label" in data
        assert "confidence" in data
        assert "recommendation" in data
        assert "request_id" in data 