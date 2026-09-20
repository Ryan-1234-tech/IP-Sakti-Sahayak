"""
IP-SAKTI Sahayak - Member 4: Multilingual & Voice Subsystem
Package initialization and high-level interface exports.
"""

from src.multilingual.pipeline import (
    process_multilingual_query,
    format_multilingual_response,
    MultilingualPipeline,
)
from src.voice.stt import transcribe_audio, SpeechToText
from src.voice.tts import synthesize_speech, TextToSpeech

__version__ = "1.0.0"
__all__ = [
    "process_multilingual_query",
    "format_multilingual_response",
    "MultilingualPipeline",
    "transcribe_audio",
    "SpeechToText",
    "synthesize_speech",
    "TextToSpeech",
]
