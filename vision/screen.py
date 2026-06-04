import ollama
import pyautogui
import base64
import tempfile
import os

def analyse_screen(question: str = "What do you see on this screen?") -> str:
    # Take screenshot
    screenshot = pyautogui.screenshot()
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        screenshot.save(f.name)
        tmp_path = f.name

    with open(tmp_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
    
    os.unlink(tmp_path)

    response = ollama.chat(
        model="llava",
        messages=[{
            "role": "user",
            "content": question,
            "images": [image_data]
        }]
    )

    return response["message"]["content"]