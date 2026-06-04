# J.A.R.V.I.S
### Just A Rather Very Intelligent System

A fully local, multi-agent AI assistant with voice interaction, Spotify control, screen vision, file generation, and real-time code execution. Built entirely in Python, running on-device with no cloud API costs.


---

## Features

| Feature | Description |
|---|---|
| 🎤 Voice Input | Whisper STT — speak naturally, Jarvis transcribes |
| 🔊 Voice Output | Piper TTS — fully local, natural-sounding responses |
| 🧠 Multi-Agent System | Commander routes requests to specialist agents |
| 🔍 Researcher Agent | Web search via DuckDuckGo + LLM synthesis |
| ✍️ Writer Agent | Documents, emails, CVs, reports |
| 💻 Coder Agent | Writes and executes Python code live |
| 🔒 Security Agent | Cybersecurity education and analysis |
| 🎵 Spotify Control | Play songs, artists, moods via voice |
| 👁️ Screen Vision | LLaVA analyses your screen on demand |
| 📄 File Generation | Creates downloadable PDF, DOCX, TXT files |
| 📎 File Upload | Upload PDFs/images for Jarvis to analyse |
| 🧬 Persistent Memory | ChromaDB vector store remembers past conversations |

---

## Architecture

User (Voice/Text)
↓
FastAPI Server
↓
Commander Agent  ──→  routes to specialist
↓
┌──────────────────────────────────────┐
│  Researcher │ Writer │ Coder │ Security │
└──────────────────────────────────────┘
↓
Tool Executor (Spotify, Apps, Files, Vision)
↓
Piper TTS → Audio Response



---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Llama 3.1 8B via Ollama |
| Vision | LLaVA via Ollama |
| Speech-to-Text | OpenAI Whisper |
| Text-to-Speech | Piper TTS |
| Memory | ChromaDB + sentence-transformers |
| Backend | FastAPI + Uvicorn |
| Frontend | Vanilla HTML/CSS/JS |
| Music | Spotify Web API |
| Search | DuckDuckGo (ddgs) |

---

## Setup

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com) installed
- [Piper TTS](https://github.com/rhasspy/piper) installed
- [FFmpeg](https://ffmpeg.org) installed
- Spotify Premium account

### Installation

```bash
# Clone the repo
git clone https://github.com/Drild/jarvis.git
cd jarvis

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Pull AI models
ollama pull llama3.1:8b
ollama pull llava
ollama pull whisper
```

### Configuration

Create a `.env` file in the root directory:

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

### Run

```bash
uvicorn server:app --reload
```

Open `http://localhost:8000` in your browser.

---

## Project Structure

jarvis/
├── server.py          # FastAPI backend
├── main.py            # Terminal interface
├── brain/
│   └── llm.py         # LLM + agent routing
├── agents/
│   ├── commander.py   # Routes to specialist agents
│   ├── researcher.py  # Web search agent
│   ├── writer.py      # Writing agent
│   ├── coder.py       # Code generation + execution
│   └── security.py    # Cybersecurity agent
├── tools/
│   ├── executor.py    # Tool dispatcher
│   ├── spotify.py     # Spotify integration
│   └── file_writer.py # PDF/DOCX/TXT generation
├── voice/
│   └── listener.py    # Whisper STT
├── vision/
│   └── screen.py      # Screen capture + LLaVA
├── memory/
│   └── remember.py    # ChromaDB vector memory
└── static/
└── index.html     # Web UI


---

## CV Bullet Points

Built a fully local multi-agent AI assistant in Python featuring voice I/O,
real-time code execution, Spotify control, screen vision, and persistent memory
Designed a Commander-Agent architecture routing user requests to specialist
agents (Researcher, Writer, Coder, Security) using Llama 3.1 8B via Ollama
Integrated ChromaDB vector embeddings for semantic long-term memory,
Whisper STT, Piper TTS, and LLaVA for multimodal screen analysis
Built a FastAPI backend with a custom Jarvis-themed web UI supporting
file upload, PDF/DOCX generation, and Spotify Web API playback control


---

## Author

**Drilden Deluc** — First Year Computer Science, Newcastle University  
[GitHub](https://github.com/Drild)