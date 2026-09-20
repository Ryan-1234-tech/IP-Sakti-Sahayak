"""
services/language.py — Language detection and translation.

Strategy (from architecture §4):
  translate-to-English-then-retrieve, translate-answer-back.

  1. Detect language of user query (fast heuristic via langdetect, fallback to LLM).
  2. If not English, translate query → English using a single LLM call.
  3. After answer is generated in English, translate answer → user's language.

This is intentionally simple — no separate translation service, no multilingual embeddings.
"""
from __future__ import annotations

import logging
from typing import Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Mapping of BCP-47 codes to human-readable language names (used in prompts)
LANGUAGE_NAMES: dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "gu": "Gujarati",
    "bn": "Bengali",
    "pa": "Punjabi",
    "ur": "Urdu",
}


def detect_language(text: str) -> str:
    """
    Detect the BCP-47 language code of a text string.

    Tries langdetect first (fast, offline). Falls back to "en" on failure.
    """
    if not text or not text.strip():
        return "en"

    try:
        from langdetect import detect, DetectorFactory

        DetectorFactory.seed = 42  # reproducible
        code = detect(text)
        return code
    except Exception as e:
        logger.debug(f"langdetect failed ({e}); defaulting to 'en'")
        return "en"


def translate_to_english(text: str, source_language: str) -> str:
    """
    Translate text from source_language to English using the LLM.

    If source_language is already English, returns text unchanged.
    """
    if source_language == "en" or source_language.startswith("en-"):
        return text

    lang_name = LANGUAGE_NAMES.get(source_language, source_language)

    from app.services.llm import complete

    prompt = (
        f"Translate the following {lang_name} text into English. "
        f"Return ONLY the English translation — no explanation, no original text.\n\n"
        f"Text to translate:\n{text}"
    )
    translated = complete(
        prompt,
        system_prompt="You are a precise translator. Return only the requested translation.",
        max_tokens=512,
        temperature=0.0,
    )
    return translated.strip()


def translate_from_english(
    text: str,
    target_language: str,
    preserve_citations: bool = True,
) -> str:
    """
    Translate an English answer into target_language using the LLM.

    If target_language is English, returns text unchanged.

    Args:
        text:               English text to translate.
        target_language:    BCP-47 code of the target language.
        preserve_citations: If True, instructs the model to keep source titles
                            in their original English form (e.g. "IP India Guidelines").
    """
    if target_language == "en" or target_language.startswith("en-"):
        return text

    lang_name = LANGUAGE_NAMES.get(target_language, target_language)

    citation_note = (
        " Keep any source titles and official document names in their original English form."
        if preserve_citations
        else ""
    )

    from app.services.llm import complete

    prompt = (
        f"Translate the following English text into {lang_name}.{citation_note} "
        f"Preserve the formatting (bullet points, numbered lists, bold text) as closely as possible. "
        f"Return ONLY the {lang_name} translation.\n\n"
        f"Text to translate:\n{text}"
    )
    translated = complete(
        prompt,
        system_prompt=f"You are a precise {lang_name} translator. Return only the {lang_name} translation.",
        max_tokens=2048,
        temperature=0.0,
    )
    return translated.strip()


def normalize_language_code(code: Optional[str]) -> str:
    """
    Normalize a language code to a simple BCP-47 tag.
    Falls back to 'en' for unsupported codes.
    """
    if not code:
        return "en"
    # Strip region suffix: "zh-CN" → "zh", "en-US" → "en"
    base = code.split("-")[0].lower()
    return base if base in LANGUAGE_NAMES else "en"
