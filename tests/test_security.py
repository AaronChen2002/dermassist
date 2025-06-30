from fastapi.testclient import TestClient
from backend.main import app

# client = TestClient(app) # This is no longer needed globally


def test_classify_lesion_invalid_key():
    """
    Tests the /classify-lesion endpoint with an invalid API key.
    It should return a 401 Unauthorized error.
    """
    with TestClient(app) as client:
        # Use a dummy image file for the test
        with open("sample_lesion.jpg", "rb") as f:
            response = client.post(
                "/classify-lesion",
                headers={"X-API-Key": "invalid-key"},
                files={"file": ("sample_lesion.jpg", f, "image/jpeg")},
            )
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid API Key"}


def test_classify_lesion_missing_key():
    """
    Tests the /classify-lesion endpoint without an API key.
    It should return a 403 Forbidden error.
    """
    with TestClient(app) as client:
        with open("sample_lesion.jpg", "rb") as f:
            response = client.post(
                "/classify-lesion",
                files={"file": ("sample_lesion.jpg", f, "image/jpeg")},
            )
        assert response.status_code == 403
        assert response.json() == {"detail": "Not authenticated"} 