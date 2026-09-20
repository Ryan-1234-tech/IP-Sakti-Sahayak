"""
Configuration module for IP-SAKTI Sahayak Multilingual & Voice Subsystem.
Loads environment variables and sets sane defaults for offline/hackathon fallback.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
AUDIO_OUTPUT_DIR = BASE_DIR / "audio_output"
AUDIO_OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

# BHASHINI Configuration (Govt of India ULCA / MeitY)
BHASHINI_USER_ID = os.getenv("BHASHINI_USER_ID", "")
BHASHINI_API_KEY = os.getenv("BHASHINI_API_KEY", "")
BHASHINI_PIPELINE_ID = os.getenv("BHASHINI_PIPELINE_ID", "")
BHASHINI_INFERENCE_URL = os.getenv(
    "BHASHINI_INFERENCE_URL",
    "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
)
ENABLE_BHASHINI_MOCK = os.getenv("ENABLE_BHASHINI_MOCK", "true").lower() in ("true", "1", "yes")

# LLM Keys (Gemini / OpenAI for advanced Hinglish code-switching normalization)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Defaults
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "hindi")
DEFAULT_RESPONSE_STYLE = os.getenv("DEFAULT_RESPONSE_STYLE", "hinglish")  # hinglish | devanagari | english

# Supported Languages in Hackathon Scope
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "code": "en", "script": "latin"},
    "hi": {"name": "Hindi", "code": "hi", "script": "devanagari"},
    "hinglish": {"name": "Hinglish", "code": "hinglish", "script": "latin"},
    "ta": {"name": "Tamil", "code": "ta", "script": "tamil"},
    "tanglish": {"name": "Tanglish", "code": "tanglish", "script": "latin"},
}
