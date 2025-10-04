import io
from gtts import gTTS

def speak(text: str):
    """
    Generate TTS audio and return a BytesIO object.
    No file is saved.
    """
    mp3_fp = io.BytesIO()
    tts = gTTS(text)
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp  # frontend can play this directly
