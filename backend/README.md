# Backend Service

This directory contains the core FastAPI backend for the DermAssist API.

## Files

- `main.py`: This is the main entry point for the FastAPI application. It defines all the API endpoints (`/classify-lesion`, `/heatmap/{request_id}`), integrates security and rate limiting, and orchestrates the application's startup logic.

- `security.py`: This module handles all authentication and authorization logic. It contains the dependency (`get_api_key`) that validates the `X-API-Key` header for protected endpoints. It also includes the custom function for per-key rate limiting.

- `config.py`: Manages all application configuration using `pydantic-settings`. It loads secrets like API keys from environment variables or a `.env` file, providing a single source of truth for settings.

- `explainability.py`: Contains the logic for generating the Grad-CAM heatmaps. It takes an image and a trained model and produces a visual overlay indicating which parts of the image were most influential in the model's prediction. 