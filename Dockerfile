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

# Install curl, create the models directory, and download the model
RUN apt-get update && apt-get install -y curl \
    && mkdir -p /app/models \
    && curl -L -o /app/models/dermassist_mobilenet_v2.pt 'https://drive.google.com/uc?export=download&id=1XTy-JO4U7Lf8UKb4YwVlNNe7ytTUJYwd' \
    && rm -rf /var/lib/apt/lists/*

# Copy the application code into the image
COPY ./backend /app/backend
COPY debug_settings.py /app/
COPY start.sh /app/

# Make the startup script executable
RUN chmod +x /app/start.sh

# Expose the port the API will run on
EXPOSE 8000

# Command to run the startup script
CMD ["/app/start.sh"]
