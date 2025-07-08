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
        print(f"DEBUG: _parse_api_keys called with: {repr(v)} (type: {type(v)})")
        
        if v is None:
            print("DEBUG: API_KEYS is None")
            raise ValueError("API_KEYS cannot be None. Please provide at least one API key.")
        
        if isinstance(v, str):
            print(f"DEBUG: Processing string value: {repr(v)}")
            # Handle empty string case
            if not v.strip():
                print("DEBUG: Empty string detected")
                raise ValueError("API_KEYS cannot be empty. Please provide at least one API key.")
            
            # Split the string by commas, strip whitespace from each key,
            # and filter out any empty strings that might result from
            # trailing commas or multiple commas.
            keys = {key.strip() for key in v.split(",") if key.strip()}
            print(f"DEBUG: Parsed keys: {keys}")
            if not keys:
                print("DEBUG: No valid keys after parsing")
                raise ValueError("API_KEYS must contain at least one valid API key.")
            return keys
        
        print(f"DEBUG: Non-string value received: {repr(v)}")
        return v


# Global settings object (will be instantiated lazily)
_settings = None

def get_settings():
    """Get the settings object (lazy instantiation)"""
    global _settings
    if _settings is None:
        try:
            _settings = Settings()
        except Exception as e:
            import sys
            print(f"CRITICAL ERROR: Failed to initialize settings: {e}")
            print(f"Available environment variables: {list(os.environ.keys())}")
            print(f"API_KEYS value: {repr(os.environ.get('API_KEYS', 'NOT_SET'))}")
            sys.exit(1)
    return _settings

# For backward compatibility, create a property-like access
class SettingsProxy:
    def __getattr__(self, name):
        return getattr(get_settings(), name)

settings = SettingsProxy() 