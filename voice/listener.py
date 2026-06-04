import whisper
import sounddevice as sd
import numpy as np
import tempfile
import scipy.io.wavfile as wav
import os

# Tell Whisper exactly where ffmpeg is
os.environ["PATH"] += r";C:\ffmpeg\ffmpeg-master-latest-win64-gpl\bin"

model = whisper.load_model("small")

def listen() -> str:
    print("🎤 Listening...")
    
    sample_rate = 16000
    duration = 7
    
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16"
    )
    sd.wait()
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav.write(f.name, sample_rate, audio)
        result = model.transcribe(f.name, language="en")
    
    text = result["text"].strip()
    print(f"You said: {text}")
    return text