"""Centralized OpenAI client construction.

This module builds an AsyncAzureOpenAI client from environment variables
and exposes a module-level `client` object and the `AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL`
value so other modules can import and reuse the same client.
"""
from dotenv import load_dotenv
import os
import sys
from openai import AsyncAzureOpenAI
from agents import set_default_openai_client

# Load .env (idempotent)
load_dotenv()

# Read relevant env vars
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL = os.getenv(
    "AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL")

missing = []
if not AZURE_OPENAI_API_KEY:
    missing.append("AZURE_OPENAI_API_KEY")
if not AZURE_OPENAI_ENDPOINT:
    missing.append("AZURE_OPENAI_ENDPOINT")
if not AZURE_OPENAI_API_VERSION:
    missing.append("AZURE_OPENAI_API_VERSION")
if not AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL:
    missing.append("AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL")

if missing:
    print("Error: missing required environment variables: " + ", ".join(missing))
    sys.exit(1)

# Narrow types for the static type checker (these asserts also act as runtime guards)
assert AZURE_OPENAI_API_KEY is not None
assert AZURE_OPENAI_ENDPOINT is not None
assert AZURE_OPENAI_API_VERSION is not None
assert AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL is not None

try:
    client = AsyncAzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_OPENAI_API_VERSION,
    )
except Exception as e:
    print(f"Error configuring Azure OpenAI client: {e}")
    # Fail fast so callers don't continue with an unconfigured client
    sys.exit(1)

# Set the library-wide default client (agents package expects this)
try:
    set_default_openai_client(client)
except Exception:
    # don't crash here if agents isn't ready; re-raise for visibility
    raise
