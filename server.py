from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from brain.llm import chat
from memory.remember import save_memory
from tools.executor import execute_tool
from tools.file_writer import save_text_file, save_docx, save_pdf, save_markdown, OUTPUT_DIR
from voice.wakeword import start_wake_word_listener
import subprocess
import tempfile
import os
import json
import base64
import fitz
import threading

app = FastAPI()

wake_triggered = False
uploaded_file_cache = {}

PIPER_EXE = r"C:\piper\piper\piper.exe"
PIPER_MODEL = r"C:\piper\piper\voices\en_US-lessac-medium.onnx"
FFMPEG = r"C:\ffmpeg\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"

os.environ["PATH"] += r";C:\ffmpeg\ffmpeg-master-latest-win64-gpl\bin"

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.get("/wake-status")
async def wake_status():
    global wake_triggered
    triggered = wake_triggered
    wake_triggered = False
    return JSONResponse({"triggered": triggered})

@app.on_event("startup")
async def startup():
    def on_wake_word():
        global wake_triggered
        wake_triggered = True
    threading.Thread(
        target=start_wake_word_listener,
        args=(on_wake_word,),
        daemon=True
    ).start()

def extract_file_content(file_bytes: bytes, filename: str) -> str:
    ext = filename.lower().split(".")[-1]
    if ext == "pdf":
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(file_bytes)
            tmp = f.name
        doc = fitz.open(tmp)
        text = "".join(page.get_text() for page in doc)
        doc.close()
        os.unlink(tmp)
        return text[:6000]
    elif ext in ["png", "jpg", "jpeg"]:
        import ollama
        image_b64 = base64.b64encode(file_bytes).decode()
        response = ollama.chat(
            model="llava",
            messages=[{
                "role": "user",
                "content": "Describe everything you see in this image in detail.",
                "images": [image_b64]
            }]
        )
        return "[IMAGE DESCRIPTION]: " + response["message"]["content"]
    elif ext == "txt":
        return file_bytes.decode("utf-8", errors="ignore")[:6000]
    return ""

def clean_reply(reply: str) -> str:
    reply = reply.strip()
    if "{" in reply:
        try:
            start = reply.index("{")
            try:
                end = reply.rindex("}") + 1
                parsed = json.loads(reply[start:end])
                return parsed.get("reply", reply)
            except Exception:
                pass
            if '"reply":' in reply:
                after = reply.split('"reply":')[1].strip()
                if after.startswith('"'):
                    content = after[1:]
                    end_idx = content.find('"')
                    if end_idx > 0:
                        return content[:end_idx]
        except Exception:
            pass
    return reply

def generate_tts(text: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as out:
        out_path = out.name
    subprocess.run([
        PIPER_EXE, "--model", PIPER_MODEL, "--output_file", out_path
    ], input=text.encode(), capture_output=True)
    with open(out_path, "rb") as f:
        audio_bytes = f.read()
    os.unlink(out_path)
    return base64.b64encode(audio_bytes).decode()

@app.post("/chat")
async def chat_endpoint(
    audio: UploadFile = File(None),
    file: UploadFile = File(None),
    text: str = Form(None)
):
    if audio:
        import whisper
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            tmp.write(await audio.read())
            tmp_path = tmp.name
        wav_path = tmp_path.replace(".webm", ".wav")
        subprocess.run([
            FFMPEG, "-y", "-i", tmp_path,
            "-ar", "16000", "-ac", "1", wav_path
        ], capture_output=True)
        model = whisper.load_model("small")
        result = model.transcribe(wav_path, language="en")
        user_input = result["text"].strip()
        os.unlink(tmp_path)
        os.unlink(wav_path)
    else:
        user_input = text or ""

    if file and file.filename:
        file_bytes = await file.read()
        file_context = extract_file_content(file_bytes, file.filename)
        if file_context:
            uploaded_file_cache[file.filename] = file_context
            user_input += f"\n\n[ATTACHED FILE: {file.filename}]\n{file_context}"
    elif uploaded_file_cache:
        for fname, content in uploaded_file_cache.items():
            user_input += f"\n\n[PREVIOUSLY UPLOADED FILE: {fname}]\n{content}"

    if not user_input.strip():
        return JSONResponse({"error": "No input received."})

    tool, argument, reply, agent = chat(user_input)
    
    # Check for news data BEFORE clean_reply
    news_data = None
    if reply.startswith("NEWS:"):
        try:
            news_data = json.loads(reply[5:])
            reply = "Here are the latest headlines."
        except:
            pass
    
    reply = clean_reply(reply)
    print(f"DEBUG — agent: {agent}, tool: {tool}, news: {news_data is not None}, reply_start: {reply[:30]}")
    
    file_path = None
    if tool and tool != "none":
        result = execute_tool(tool, argument)
        if tool in ["save_txt", "save_docx", "save_pdf"]:
            file_path = result.replace("Saved to ", "").strip()
        elif tool in ["get_weather", "get_weather_detailed"]:
            reply = result

    save_memory(user_input[:200], reply)

    audio_b64 = generate_tts(reply)
    display_input = user_input.split("\n\n[")[0]

    return JSONResponse({
        "user": display_input[:300],
        "reply": reply,
        "tool": tool,
        "agent": agent,
        "audio": audio_b64,
        "file_path": file_path,
        "news" : news_data
    })

@app.get("/download")
def download_file(path: str = Query(...)):
    path = path.strip()
    if not os.path.exists(path):
        return JSONResponse({"error": "File not found"})
    if not path.startswith(OUTPUT_DIR):
        return JSONResponse({"error": "Invalid path"})
    return FileResponse(
        path,
        filename=os.path.basename(path),
        media_type="application/octet-stream"
    )