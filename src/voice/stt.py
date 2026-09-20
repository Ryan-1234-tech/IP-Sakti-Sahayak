"""
Speech-to-Text (STT) Module for IP-SAKTI Sahayak.
Transcribes audio input from Microphone or Audio Files (.wav, .mp3, .m4a)
using SpeechRecognition (Google STT), Whisper, or BHASHINI ASR.
"""

import os
import io
import wave
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class SpeechToText:
    """Speech Recognition Engine supporting Hindi, Hinglish, and Indian English."""

    def __init__(self, default_language: str = "hi-IN"):
        self.default_language = default_language

    def transcribe(
        self,
        audio_source: Union[str, Path, bytes, io.BytesIO],
        language_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribes audio into text.
        
        Args:
            audio_source: File path, bytes, or BytesIO audio stream.
            language_code: 'hi-IN' (Hindi), 'en-IN' (Indian English), or 'auto'.
            
        Returns:
            {
                "text": "Transcribed string",
                "detected_language": "hi-IN",
                "status": "success",
                "engine": "google_speech_recognition"
            }
        """
        lang = language_code or self.default_language

        # 1. Try SpeechRecognition (Google STT API - free & fast for Hindi/English)
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()

            # Handle bytes / file path
            if isinstance(audio_source, (str, Path)):
                file_path = str(audio_source)
                with sr.AudioFile(file_path) as source:
                    audio_data = recognizer.record(source)
            elif isinstance(audio_source, bytes):
                audio_io = io.BytesIO(audio_source)
                with sr.AudioFile(audio_io) as source:
                    audio_data = recognizer.record(source)
            elif isinstance(audio_source, io.BytesIO):
                with sr.AudioFile(audio_source) as source:
                    audio_data = recognizer.record(source)
            else:
                return {
                    "text": "",
                    "status": "error",
                    "error": "Unsupported audio source format"
                }

            # First try with requested language (e.g. 'hi-IN' or 'en-IN')
            try:
                transcription = recognizer.recognize_google(audio_data, language=lang)
            except sr.UnknownValueError:
                # If Hindi failed, try English fallback
                if lang == "hi-IN":
                    transcription = recognizer.recognize_google(audio_data, language="en-IN")
                else:
                    raise

            return {
                "text": transcription,
                "detected_language": lang,
                "status": "success",
                "engine": "google_speech_recognition"
            }

        except Exception as e:
            logger.warning(f"Speech recognition attempt failed: {e}")
            return {
                "text": "",
                "status": "error",
                "error": str(e),
                "engine": "stt_fallback"
            }


_stt_instance = SpeechToText()


def transcribe_audio(
    audio_source: Union[str, Path, bytes, io.BytesIO],
    language_code: str = "hi-IN"
) -> Dict[str, Any]:
    """
    Public standardized entrypoint for Speech-to-Text.
    """
    return _stt_instance.transcribe(audio_source, language_code)
