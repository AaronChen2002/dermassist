from typing import Set

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    These are loaded from a .env file or environment variables.
    """

    # Pydantic V2 model configuration
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
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
            # Split the string by commas, strip whitespace from each key,
            # and filter out any empty strings that might result from
            # trailing commas or multiple commas.
            return {key.strip() for key in v.split(",") if key.strip()}
        return v


# Instantiate the settings object that will be used across the application
settings = Settings() 