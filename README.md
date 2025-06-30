# DermAssist: Tele-Derm Triage API

## Project Overview

**DermAssist** is a tele-dermatology triage service that enables clinicians to upload patient skin lesion photos, receive a preliminary classification (e.g., eczema, psoriasis, melanoma), and view an explainability heatmap indicating model attention. This API-driven product bridges the gap in remote dermatology care by providing quick, data-driven support for referral decisions.

## Key Objectives

1. **Accurate Classification**: Fine-tune a lightweight CNN (MobileNetV2) on the HAM10000 dataset to classify common dermatological conditions.
2. **Explainability**: Generate Grad-CAM heatmaps so clinicians can visualize why the model made a certain prediction.
3. **Seamless Integration**: Expose RESTful endpoints for classification, heatmap retrieval, and API-key based authentication.
4. **Production-Ready**: Containerize, deploy to Render (backend) and Vercel (optional frontend demo), with CI/CD pipelines and rate limiting.

## Feature List

* **`POST /classify-lesion`**: Upload image, return JSON with `label`, `confidence`, and `recommendation`.
* **`GET /heatmap/{request_id}`**: Retrieve Grad-CAM overlay image for explainability.
* **API Key Auth**: Middleware to enforce per-request authorization.
* **Rate Limiting**: 100 requests/day per key.
* **Optional Demo Frontend**: React component for drag-and-drop image testing.

---

## Local Development

### Setup

1.  **Create Conda Environment**:
    ```bash
    conda create --name dermassist python=3.11 -y
    ```

2.  **Install Dependencies**:
    All dependencies are listed in `requirements.txt`. Install them into the new environment:
    ```bash
    conda run -n dermassist pip install -r requirements.txt
    ```

### Running the Tests

To verify the application is working correctly, run the test suite using `pytest`:

```bash
conda run -n dermassist pytest
```

### Running the Application

To run the application locally (without Docker), you can use `uvicorn`:

```bash
conda run -n dermassist uvicorn backend.main:app --reload
```

---

## Development Status

**Current Phase:** Phase 3: Foundational Testing

**Last Completed Step:**
- The backend application has been fully containerized using Docker (`Dockerfile`).
- A `docker-compose.yml` file has been created to manage the application stack (backend + redis).
- All code for this phase has been written.

**Current Blocker:**
- We are in the final verification step for Phase 2.
- When running the application via `docker-compose`, the API is serving a stale, placeholder response instead of the latest code that uses the real ML model.
- We suspect this is a Docker caching issue.

**Immediate Next Step:**
- The next action is to perform a clean rebuild of the Docker images to resolve the caching problem. The proposed command sequence is:
  1. `docker-compose down`
  2. `docker-compose build --no-cache`
  3. `docker-compose up -d`
  4. Retest the `/classify-lesion` endpoint.