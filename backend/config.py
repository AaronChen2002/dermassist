from typing import Set, Optional
import os

from pydantic import field_validator, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    These are loaded from a .env file or environment variables.
    """

    # Pydantic V2 model configuration
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        case_sensitive=False,
        env_prefix="",  # No prefix for environment variables
        extra="ignore"  # Ignore extra environment variables
    )

    # A set of allowed API keys.
    # In the environment, this should be a comma-separated string.
    # Example: API_KEYS="key1,key2,key3"
    API_KEYS: Set[str]

    # The connection URL for the Redis instance.
    REDIS_URL: str

    @field_validator("API_KEYS", mode="before")
    @classmethod
    def _parse_api_keys(cls, v):
        """Parse a comma-separated string of API keys into a set."""
        if isinstance(v, str):
            # Handle empty string case
            if not v.strip():
                raise ValueError("API_KEYS cannot be empty. Please provide at least one API key.")
            
            # Split the string by commas, strip whitespace from each key,
            # and filter out any empty strings that might result from
            # trailing commas or multiple commas.
            keys = {key.strip() for key in v.split(",") if key.strip()}
            if not keys:
                raise ValueError("API_KEYS must contain at least one valid API key.")
            return keys
        return v


# Instantiate the settings object that will be used across the application
try:
    settings = Settings()
except Exception as e:
    import sys
    print(f"CRITICAL ERROR: Failed to initialize settings: {e}")
    print(f"Available environment variables: {list(os.environ.keys())}")
    sys.exit(1) 