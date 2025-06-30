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