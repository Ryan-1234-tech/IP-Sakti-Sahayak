"""
Microphone Audio Recorder Utility for IP-SAKTI Sahayak.
Records audio from microphone and saves to .wav file for STT testing.
"""

import io
import wave
import logging
from typing import Optional
from pathlib import Path
from src import config

logger = logging.getLogger(__name__)


def record_audio_from_mic(
    duration_seconds: int = 5,
    output_filename: Optional[str] = None
) -> Optional[str]:
    """
    Records audio from the default microphone.
    
    Args:
        duration_seconds: Duration to record in seconds.
        output_filename: Output path for WAV file.
        
    Returns:
        Path to the saved WAV file or None if microphone unavailable.
    """
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            logger.info("Adjusting for ambient noise... Please wait.")
            r.adjust_for_ambient_noise(source, duration=1)
            logger.info(f"Recording for {duration_seconds} seconds... Speak now!")
            audio = r.record(source, duration=duration_seconds)

        out_path = output_filename or str(config.AUDIO_OUTPUT_DIR / "mic_recording.wav")
        with open(out_path, "wb") as f:
            f.write(audio.get_wav_data())

        logger.info(f"Recording saved to: {out_path}")
        return out_path

    except Exception as e:
        logger.warning(f"Microphone recording failed (maybe no mic attached or headless): {e}")
        return None
