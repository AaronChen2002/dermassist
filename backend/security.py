from fastapi import Security, HTTPException, status, Request
from fastapi.security import APIKeyHeader
import logging

from .config import settings

# --- API Key Authentication ---
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# --- Rate Limit Key Function ---
def get_api_key_for_rate_limiting(request: Request) -> str:
    """
    Returns the API key from the request header for rate limiting purposes.
    Falls back to the client's host IP if the key is not present.
    """
    api_key = request.headers.get(API_KEY_NAME)
    return api_key or request.client.host

async def get_api_key(api_key: str = Security(api_key_header)):
    """
    Dependency to verify the API key provided in the request header.
    
    Raises:
        HTTPException: If the API key is invalid or not provided.
    """
    if api_key in settings.API_KEYS:
        return api_key
    else:
        logging.warning(f"Invalid API Key received: {api_key}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        ) 