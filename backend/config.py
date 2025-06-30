from pydantic_settings import BaseSettings
from typing import Set

class Settings(BaseSettings):
    """
    Manages application configuration using Pydantic.
    Reads settings from environment variables or a .env file.
    """
    # A set of predefined, allowable API keys.
    # In a real-world application, these would be loaded from a secure
    # environment variable or a secret management service.
    # Example: API_KEYS="key1,key2,key3"
    API_KEYS: Set[str] = {"default-key-for-testing"}

    class Config:
        # Pydantic-settings will automatically look for a .env file
        # in the same directory and load variables from it.
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Instantiate the settings object that will be used across the application
settings = Settings() 