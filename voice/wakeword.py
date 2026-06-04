import threading
import numpy as np
import pyaudio
from openwakeword.model import Model

model = Model(inference_framework="onnx")

def listen_for_wake_word(callback):
    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=16000,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=1280
    )

    print("👂 Listening for wake word: 'Hey Jarvis'...")

    try:
        while True:
            audio = stream.read(1280, exception_on_overflow=False)
            audio_np = np.frombuffer(audio, dtype=np.int16)
            prediction = model.predict(audio_np)

            for wake_word, score in prediction.items():
                if score > 0.5:
                    print(f"🔔 Wake word detected: {wake_word} ({score:.2f})")
                    callback()
                    import time
                    time.sleep(2)
    except Exception as e:
        print(f"Wake word error: {str(e)}")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

def start_wake_word_listener(callback):
    thread = threading.Thread(target=listen_for_wake_word, args=(callback,), daemon=True)
    thread.start()
    return thread