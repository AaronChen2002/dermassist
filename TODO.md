# Project TODO List

This file tracks pending tasks and items that need to be revisited.

- [x] **Fix Docker Caching Issue & Verify Setup**: 
  - **Problem**: The running Docker container is serving stale application code, returning a placeholder API response instead of real model predictions. This is likely a Docker caching issue.
  - **Plan**:
    1. Stop and remove the current containers: `docker-compose down`
    2. Force a clean rebuild without cache: `docker-compose build --no-cache`
    3. Restart the services: `docker-compose up -d`
    4. Verify the fix by sending a test request to the `/classify-lesion` endpoint.

- [ ] **Verify Docker Setup**: The Docker build failed due to a local authentication issue with Docker Desktop. Once the login issue is resolved, we need to:
  1. Run `docker build -t dermassist-api .` to confirm the image builds successfully.
  2. Run `docker-compose up` to confirm the full application stack (backend + redis) starts and runs correctly. 