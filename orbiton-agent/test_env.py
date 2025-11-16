#!/usr/bin/env python3
"""Test script to verify environment variables are loaded correctly."""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("=" * 60)
print("Environment Variables Test")
print("=" * 60)

# Check OPENAI_API_KEY
openai_key = os.getenv("OPENAI_API_KEY")
print(f"OPENAI_API_KEY: {openai_key[:10]}..." if openai_key else "OPENAI_API_KEY: NOT SET ❌")

# Check BASE_URL
base_url = os.getenv("BASE_URL")
print(f"BASE_URL: {base_url if base_url else 'NOT SET ❌'}")

# Check model overrides
model = os.getenv("ORBITON_LLM_MODEL")
print(f"ORBITON_LLM_MODEL: {model if model else 'Not set (will use default)'}")

provider = os.getenv("ORBITON_LLM_PROVIDER")
print(f"ORBITON_LLM_PROVIDER: {provider if provider else 'Not set (will use default)'}")

print("=" * 60)

# Test if variables are accessible
if not openai_key:
    print("\n⚠️  WARNING: OPENAI_API_KEY is not set!")
    print("Make sure your .env file has:")
    print("OPENAI_API_KEY=your-actual-key")
    print("\nNOTE: It's OPENAI_API_KEY (no underscore between OPEN and AI)")
elif openai_key.startswith("sk-"):
    print("\n✅ API key format looks correct (starts with sk-)")
else:
    print(f"\n⚠️  API key doesn't start with 'sk-': {openai_key[:20]}")

if base_url:
    print(f"\n✅ BASE_URL is set: {base_url}")
else:
    print("\n⚠️  BASE_URL is not set (will use default)")

print("=" * 60)
