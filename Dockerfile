# --- Stage 1: Builder ---
# This stage installs dependencies and builds wheels.
FROM python:3.11-slim AS builder

WORKDIR /app

# Upgrade pip and install wheel
RUN pip install --upgrade pip wheel

# Copy requirements and build wheels for faster installation in the final stage
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt


# --- Stage 2: Final Image ---
# This stage creates the final, lean production image.
FROM python:3.11-slim

WORKDIR /app

# Copy the pre-built wheels from the builder stage
COPY --from=builder /app/wheels /wheels
COPY requirements.txt .

# Install dependencies from the local wheels
# This is much faster and more reliable than downloading from PyPI again.
RUN pip install --no-cache /wheels/*

# Copy the application code and the trained model into the image
COPY ./backend /app/backend
COPY ./models /app/models

# Expose the port the API will run on
EXPOSE 8000

# Command to run the application using uvicorn
# The --host 0.0.0.0 makes the server accessible from outside the container.
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
