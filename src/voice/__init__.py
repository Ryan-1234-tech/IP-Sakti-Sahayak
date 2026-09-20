"""
Voice Subsystem for IP-SAKTI Sahayak (Speech-to-Text & Text-to-Speech).
"""

try:
    from src.voice.stt import transcribe_audio, SpeechToText
    from src.voice.tts import synthesize_speech, TextToSpeech
    from src.voice.recorder import record_audio_from_mic
except (ImportError, ModuleNotFoundError):
    from voice.stt import transcribe_audio, SpeechToText
    from voice.tts import synthesize_speech, TextToSpeech
    from voice.recorder import record_audio_from_mic

__all__ = [
    "transcribe_audio",
    "SpeechToText",
    "synthesize_speech",
    "TextToSpeech",
    "record_audio_from_mic",
]
