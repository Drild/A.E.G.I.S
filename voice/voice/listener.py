import whisper
import sounddevice as sd
import numpy as np
import tempfile
import scipy.io.wavfile as wav
import os

os.environ["PATH"] += r";C:\ffmpeg\ffmpeg-master-latest-win64-gpl\bin"

model = whisper.load_model("small")

def listen() -> str:
    print("🎤 Listening...")

    sample_rate = 16000
    silence_threshold = 500  # volume level considered silence
    silence_duration = 1.5   # seconds of silence before stopping
    max_duration = 10         # max recording time in seconds

    chunk_size = int(sample_rate * 0.1)  # 100ms chunks
    max_chunks = int(max_duration / 0.1)
    silence_chunks = int(silence_duration / 0.1)

    audio_chunks = []
    silent_count = 0
    started_speaking = False

    for _ in range(max_chunks):
        chunk = sd.rec(chunk_size, samplerate=sample_rate, channels=1, dtype="int16")
        sd.wait()
        audio_chunks.append(chunk)

        volume = np.abs(chunk).mean()

        if volume > silence_threshold:
            started_speaking = True
            silent_count = 0
        elif started_speaking:
            silent_count += 1
            if silent_count >= silence_chunks:
                print("🔇 Silence detected, stopping...")
                break

    audio = np.concatenate(audio_chunks, axis=0)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav.write(f.name, sample_rate, audio)
        result = model.transcribe(f.name, language="en")
        os.unlink(f.name)

    text = result["text"].strip()
    print(f"You said: {text}")
    return text