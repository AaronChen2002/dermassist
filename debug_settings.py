#!/usr/bin/env python3
"""
Diagnostic script to test environment variable loading and settings parsing.
Run this in your deployment environment to debug issues.
"""

import os
import sys
from typing import Set

print("=== Environment Variable Diagnostic ===")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")

# Print all environment variables
print("\n=== All Environment Variables ===")
for key, value in sorted(os.environ.items()):
    if "API" in key or "REDIS" in key:
        print(f"{key} = {value}")

# Test API_KEYS specifically
print("\n=== API_KEYS Testing ===")
api_keys_raw = os.environ.get("API_KEYS", "NOT_SET")
print(f"Raw API_KEYS value: {repr(api_keys_raw)}")
print(f"Type: {type(api_keys_raw)}")
print(f"Length: {len(api_keys_raw) if api_keys_raw != 'NOT_SET' else 'N/A'}")

if api_keys_raw != "NOT_SET":
    # Test the parsing logic
    try:
        if isinstance(api_keys_raw, str):
            if not api_keys_raw.strip():
                print("ERROR: API_KEYS is empty string")
            else:
                keys = {key.strip() for key in api_keys_raw.split(",") if key.strip()}
                print(f"Parsed keys: {keys}")
                print(f"Number of keys: {len(keys)}")
    except Exception as e:
        print(f"ERROR parsing API_KEYS: {e}")

# Test pydantic-settings import
print("\n=== Pydantic Settings Test ===")
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import field_validator
    print("✅ Pydantic imports successful")
    
    # Test settings creation
    class TestSettings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=".env", 
            env_file_encoding="utf-8", 
            case_sensitive=False,
            env_prefix="",
            extra="ignore"
        )
        
        API_KEYS: Set[str]
        REDIS_URL: str = "redis://localhost:6379"
        
        @field_validator("API_KEYS", mode="before")
        @classmethod
        def _parse_api_keys(cls, v):
            print(f"Validator received: {repr(v)} (type: {type(v)})")
            if isinstance(v, str):
                if not v.strip():
                    raise ValueError("API_KEYS cannot be empty. Please provide at least one API key.")
                keys = {key.strip() for key in v.split(",") if key.strip()}
                if not keys:
                    raise ValueError("API_KEYS must contain at least one valid API key.")
                return keys
            return v
    
    print("✅ Test settings class created")
    
    # Try to instantiate
    test_settings = TestSettings()
    print("✅ Test settings instantiated successfully")
    print(f"API_KEYS: {test_settings.API_KEYS}")
    print(f"REDIS_URL: {test_settings.REDIS_URL}")
    
except Exception as e:
    print(f"❌ Error with pydantic settings: {e}")
    import traceback
    traceback.print_exc()

# Test Redis connection
print("\n=== Redis Connection Test ===")
try:
    import redis
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    print(f"Redis URL: {redis_url}")
    
    r = redis.from_url(redis_url)
    r.ping()
    print("✅ Redis connection successful")
except Exception as e:
    print(f"❌ Redis connection failed: {e}")

print("\n=== Diagnostic Complete ===") 