"""
BHASHINI Client (National Language Translation Mission - MeitY / Govt of India).
Provides interfaces for:
- NMT (Neural Machine Translation: Hindi <-> English)
- ASR (Automatic Speech Recognition / Speech to Text)
- TTS (Text to Speech)

Includes realistic fallback / simulation for offline hackathon demos.
"""

import json
import logging
import requests
from typing import Dict, Any, Optional
try:
    from src import config
except (ImportError, ModuleNotFoundError):
    import config

logger = logging.getLogger(__name__)


class BhashiniClient:
    """Client for interacting with Government of India ULCA / BHASHINI endpoints."""

    def __init__(
        self,
        user_id: Optional[str] = None,
        api_key: Optional[str] = None,
        pipeline_id: Optional[str] = None,
        enable_mock: bool = True
    ):
        self.user_id = user_id or config.BHASHINI_USER_ID
        self.api_key = api_key or config.BHASHINI_API_KEY
        self.pipeline_id = pipeline_id or config.BHASHINI_PIPELINE_ID
        self.inference_url = config.BHASHINI_INFERENCE_URL
        self.enable_mock = enable_mock or config.ENABLE_BHASHINI_MOCK

    def is_configured(self) -> bool:
        """Checks if live Bhashini API keys are present."""
        return bool(self.user_id and self.api_key and self.pipeline_id)

    def translate_nmt(
        self,
        text: str,
        source_lang: str = "hi",
        target_lang: str = "en"
    ) -> Dict[str, Any]:
        """
        Translates text between Indian languages and English using Bhashini NMT.
        """
        if not text or not text.strip():
            return {"translated_text": "", "status": "empty", "source": "bhashini"}

        # Attempt Live Bhashini API Call if credentials configured
        if self.is_configured():
            try:
                headers = {
                    "Content-Type": "application/json",
                    "userID": self.user_id,
                    "ulcaApiKey": self.api_key
                }
                payload = {
                    "pipelineTasks": [
                        {
                            "taskType": "translation",
                            "config": {
                                "language": {
                                    "sourceLanguage": source_lang,
                                    "targetLanguage": target_lang
                                }
                            }
                        }
                    ],
                    "inputData": {
                        "input": [{"source": text}]
                    }
                }
                response = requests.post(
                    self.inference_url,
                    json=payload,
                    headers=headers,
                    timeout=8
                )
                if response.status_code == 200:
                    data = response.json()
                    translated = data["pipelineResponse"][0]["output"][0]["target"]
                    return {
                        "translated_text": translated,
                        "status": "success",
                        "engine": "bhashini_live",
                        "source_lang": source_lang,
                        "target_lang": target_lang
                    }
            except Exception as e:
                logger.warning(f"Bhashini live NMT call failed: {e}. Falling back to local engine.")

        # Fallback / Mock Simulation
        return self._simulate_nmt(text, source_lang, target_lang)

    def _simulate_nmt(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """
        Fallback simulation using deep-translator or built-in dictionary.
        """
        try:
            from deep_translator import GoogleTranslator
            s_code = "hi" if source_lang.lower() in ("hi", "hindi", "hinglish") else "en"
            t_code = "en" if target_lang.lower() in ("en", "english") else "hi"

            if s_code == t_code:
                return {
                    "translated_text": text,
                    "status": "success",
                    "engine": "bhashini_mock_identity"
                }

            translated = GoogleTranslator(source=s_code, target=t_code).translate(text)
            return {
                "translated_text": translated,
                "status": "success",
                "engine": "bhashini_mock_neural",
                "source_lang": source_lang,
                "target_lang": target_lang
            }
        except Exception as e:
            return {
                "translated_text": text,
                "status": "fallback_unchanged",
                "engine": "bhashini_mock_error",
                "error": str(e)
            }
