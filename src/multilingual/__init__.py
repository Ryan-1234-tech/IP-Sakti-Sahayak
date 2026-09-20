"""
Multilingual package for IP-SAKTI Sahayak.
"""

from src.multilingual.detector import detect_language_and_script
from src.multilingual.normalizer import QueryNormalizer
from src.multilingual.translator import ResponseTranslator
from src.multilingual.bhashini_client import BhashiniClient
from src.multilingual.pipeline import (
    process_multilingual_query,
    format_multilingual_response,
    MultilingualPipeline,
)

__all__ = [
    "detect_language_and_script",
    "QueryNormalizer",
    "ResponseTranslator",
    "BhashiniClient",
    "process_multilingual_query",
    "format_multilingual_response",
    "MultilingualPipeline",
]
