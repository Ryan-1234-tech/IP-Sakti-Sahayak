"""
Main Multilingual Pipeline Interface for IP-SAKTI Sahayak.
Provides standardized functions:
- process_multilingual_query(text, language)
- format_multilingual_response(english_response, target_language, style)
"""

from typing import Dict, Any, Optional
try:
    from src.multilingual.detector import detect_language_and_script
    from src.multilingual.normalizer import QueryNormalizer
    from src.multilingual.translator import ResponseTranslator
    from src import config
except (ImportError, ModuleNotFoundError):
    from multilingual.detector import detect_language_and_script
    from multilingual.normalizer import QueryNormalizer
    from multilingual.translator import ResponseTranslator
    import config


class MultilingualPipeline:
    """End-to-end Multilingual Pipeline coordinating detection, normalization, and translation."""

    def __init__(self, use_llm: bool = True):
        self.normalizer = QueryNormalizer(use_llm=use_llm)
        self.translator = ResponseTranslator(use_llm=use_llm)

    def process_query(self, text: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Processes an incoming query in Hindi / Hinglish / English.
        Returns normalized English query for RAG along with detected metadata.
        """
        if not text:
            return {
                "original_query": "",
                "normalized_query": "",
                "language": language or "English",
                "detected_language": "english",
                "detected_script": "latin",
                "confidence": 1.0,
                "intent_category": "none",
                "extracted_keywords": [],
                "target_response_language": "hindi",
                "target_response_style": "hinglish"
            }

        # 1. Detection
        detected = detect_language_and_script(text)
        detected_lang = detected["language"]
        detected_script = detected["script"]

        # Override if user explicitly specified
        active_lang = language.lower() if language else detected_lang

        # 2. Normalization
        norm_result = self.normalizer.normalize(text, detected)

        # 3. Determine target response formatting
        if active_lang in ("hindi", "hi"):
            target_resp_lang = "hindi"
            target_resp_style = "devanagari" if detected_script == "devanagari" else "hinglish"
        elif active_lang in ("hinglish",):
            target_resp_lang = "hindi"
            target_resp_style = "hinglish"
        elif active_lang in ("tamil", "tanglish", "ta"):
            target_resp_lang = "tamil"
            target_resp_style = "devanagari"
        else:
            target_resp_lang = "english"
            target_resp_style = "english"

        # Format user-facing language name
        display_language = active_lang.capitalize()
        if active_lang == "hinglish":
            display_language = "Hinglish (Hindi-English)"
        elif active_lang == "hindi":
            display_language = "Hindi"

        return {
            "original_query": text,
            "normalized_query": norm_result["normalized_query"],
            "language": display_language,
            "detected_language": detected_lang,
            "detected_script": detected_script,
            "confidence": detected.get("confidence", 0.9),
            "is_code_mixed": detected.get("is_code_mixed", False),
            "intent_category": norm_result.get("intent_category", "general_inquiry"),
            "extracted_keywords": norm_result.get("extracted_keywords", []),
            "target_response_language": target_resp_lang,
            "target_response_style": target_resp_style,
            "engine": norm_result.get("engine", "default")
        }

    def format_response(
        self,
        english_response: str,
        target_language: str = "hindi",
        style: str = "hinglish"
    ) -> Dict[str, Any]:
        """
        Converts the English RAG response back into the user's preferred language & style.
        """
        localized = self.translator.localize_response(
            english_text=english_response,
            target_language=target_language,
            style=style
        )
        return {
            "original_english_response": english_response,
            "localized_response": localized["localized_text"],
            "language": localized["language"],
            "style": localized["style"],
            "engine": localized["engine"]
        }


# Global singleton instance
_pipeline_instance = MultilingualPipeline()


def process_multilingual_query(text: str, language: Optional[str] = None) -> Dict[str, Any]:
    """
    Public standardized entrypoint for Member 4:
    
    Example:
    >>> process_multilingual_query("Maine Ayurvedic medicine banayi hai, isko patent kaise karu?")
    {
        "normalized_query": "How can I patent my Ayurvedic medicine in India?",
        "language": "Hinglish (Hindi-English)",
        "detected_language": "hinglish",
        "target_response_language": "hindi",
        "target_response_style": "hinglish"
    }
    """
    return _pipeline_instance.process_query(text, language)


def format_multilingual_response(
    english_response: str,
    target_language: str = "hindi",
    style: str = "hinglish"
) -> Dict[str, Any]:
    """
    Public standardized entrypoint to translate RAG response into Hindi / Hinglish.
    """
    return _pipeline_instance.format_response(english_response, target_language, style)
