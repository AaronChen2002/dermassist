#!/usr/bin/env python3
import os

print("=== Simple API_KEYS Test ===")
api_keys = os.environ.get("API_KEYS", "NOT_SET")
print(f"API_KEYS value: {repr(api_keys)}")
print(f"Length: {len(api_keys) if api_keys != 'NOT_SET' else 'N/A'}")
print(f"Type: {type(api_keys)}")

if api_keys != "NOT_SET":
    print(f"First 10 chars: {repr(api_keys[:10])}")
    print(f"Last 10 chars: {repr(api_keys[-10:])}")
    has_quotes = '"' in api_keys
    has_newlines = '\n' in api_keys
    print(f"Contains quotes: {has_quotes}")
    print(f"Contains newlines: {has_newlines}")
    print(f"Stripped: {repr(api_keys.strip())}") 