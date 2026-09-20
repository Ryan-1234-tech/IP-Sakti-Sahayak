"""
Text-to-Speech (TTS) Module for IP-SAKTI Sahayak.
Synthesizes Hindi, Hinglish, and English text into natural voice audio using gTTS.
"""

import os
import uuid
import base64
import logging
from typing import Dict, Any, Optional
from pathlib import Path
try:
    from src import config
except (ImportError, ModuleNotFoundError):
    import config

logger = logging.getLogger(__name__)


class TextToSpeech:
    """TTS Engine using Google Text-to-Speech (gTTS) with Indian voice presets."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or config.AUDIO_OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def synthesize(
        self,
        text: str,
        language: str = "hi",
        tld: str = "co.in",
        slow: bool = False
    ) -> Dict[str, Any]:
        """
        Synthesizes text into an MP3 voice file.
        
        Args:
            text: Text to synthesize (Hindi Devanagari, Hinglish, or English).
            language: 'hi' for Hindi, 'en' for English.
            tld: 'co.in' for Indian English accent.
            slow: Whether to speak slowly.
            
        Returns:
            {
                "audio_path": "/path/to/audio.mp3",
                "filename": "audio_123.mp3",
                "audio_base64": "...",
                "language": language,
                "status": "success"
            }
        """
        clean_text = text.strip()
        if not clean_text:
            return {"status": "error", "error": "Empty text for speech synthesis"}

        # Strip markdown symbols for cleaner TTS reading
        speech_text = self._sanitize_text_for_tts(clean_text)

        # Determine language code for gTTS
        lang_code = "hi" if language.lower() in ("hi", "hindi", "hinglish") else "en"

        filename = f"response_{uuid.uuid4().hex[:8]}.mp3"
        output_path = self.output_dir / filename

        try:
            from gtts import gTTS
            tts = gTTS(text=speech_text, lang=lang_code, tld=tld, slow=slow)
            tts.save(str(output_path))

            # Read base64 for web/frontend streaming
            with open(output_path, "rb") as f:
                audio_bytes = f.read()
                b64_data = base64.b64encode(audio_bytes).decode("utf-8")

            return {
                "audio_path": str(output_path),
                "filename": filename,
                "audio_base64": b64_data,
                "language": lang_code,
                "status": "success",
                "engine": "gtts"
            }

        except Exception as e:
            logger.warning(f"gTTS generation failed: {e}")
            return {
                "audio_path": None,
                "filename": None,
                "audio_base64": None,
                "status": "error",
                "error": str(e),
                "engine": "tts_error"
            }

    def _sanitize_text_for_tts(self, text: str) -> str:
        """Removes markdown asterisks, hashes, urls, and bracket links for clean speech."""
        import re
        # Remove bold/italics
        t = re.sub(r'[*_#`~]', '', text)
        # Remove markdown links [text](url) -> text
        t = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', t)
        # Remove bullet points
        t = re.sub(r'^\s*[-•*]\s+', '', t, flags=re.MULTILINE)
        # Collapse multiple newlines/spaces
        t = re.sub(r'\n+', '. ', t)
        t = re.sub(r'\s+', ' ', t).strip()
        return t


_tts_instance = TextToSpeech()


def synthesize_speech(
    text: str,
    language: str = "hi",
    slow: bool = False
) -> Dict[str, Any]:
    """
    Public standardized entrypoint for Text-to-Speech.
    """
    return _tts_instance.synthesize(text, language=language, slow=slow)
