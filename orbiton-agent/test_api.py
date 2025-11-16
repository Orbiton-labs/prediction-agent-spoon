#!/usr/bin/env python3
"""Test if API key is being sent correctly in requests."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

print("=" * 60)
print("API Configuration Test")
print("=" * 60)

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("BASE_URL")
model = os.getenv("ORBITON_LLM_MODEL")

print(f"API Key: {api_key[:20]}..." if api_key else "NOT SET")
print(f"Base URL: {base_url}")
print(f"Model: {model}")
print("=" * 60)

# Test with httpx (what OpenAI library uses)
try:
    import httpx

    print("\nTesting API endpoint...")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    print(f"\nRequest Headers:")
    print(f"  Authorization: Bearer {api_key[:20]}...")
    print(f"  Content-Type: application/json")
    print(f"\nEndpoint: {base_url}/models")

    # Try to list models
    response = httpx.get(
        f"{base_url}/models",
        headers=headers,
        timeout=10.0
    )

    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")

    if response.status_code == 200:
        print("\n✅ API key is working!")
        print(f"Response: {response.text[:200]}...")
    else:
        print(f"\n❌ API request failed")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"\n❌ Error testing API: {e}")
    print(f"Error type: {type(e).__name__}")

print("=" * 60)
