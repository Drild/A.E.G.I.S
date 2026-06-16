<div align="center">

<h1>
  <img src="https://img.shields.io/badge/A.E.G.I.S-Autonomous%20Expert%20Guardian%20Intelligence%20System-00d4ff?style=for-the-badge&labelColor=020408&color=00d4ff" alt="A.E.G.I.S"/>
</h1>

<p>
  <strong>A fully local, multi-agent AI assistant — built from scratch with Python, FastAPI, and Ollama.</strong><br/>
  Voice-activated. GPU-accelerated. No cloud. No subscriptions. Runs entirely on your machine.
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.11-00d4ff?style=flat-square&logo=python&logoColor=white&labelColor=020408"/>
  <img src="https://img.shields.io/badge/FastAPI-0.115-00d4ff?style=flat-square&logo=fastapi&logoColor=white&labelColor=020408"/>
  <img src="https://img.shields.io/badge/Ollama-LLaMA%203.1%208B-00d4ff?style=flat-square&labelColor=020408"/>
  <img src="https://img.shields.io/badge/NVIDIA-GPU%20Accelerated-00d4ff?style=flat-square&logo=nvidia&logoColor=white&labelColor=020408"/>
  <img src="https://img.shields.io/badge/Local-No%20Cloud-00ff88?style=flat-square&labelColor=020408"/>
</p>

<p>
  <a href="#-demo">Demo</a> •
  <a href="#-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-setup">Setup</a> •
  <a href="#-tech-stack">Tech Stack</a>
</p>

> ⚠️ **Note:** A GIF demo will be added here shortly. See [Features](#-features) for a full breakdown.

</div>

---

## What is A.E.G.I.S?

A.E.G.I.S is a personal AI assistant that runs **entirely locally** — no OpenAI, no API keys, no data leaving your machine. It uses a **multi-agent architecture** where a Commander agent routes your requests to specialist agents (Researcher, Writer, Coder, Security, Finance), each with their own conversation history and system prompt.

Built as a portfolio project by a first-year Computer Science (Cybersecurity) student at Newcastle University, it demonstrates real-world integration of LLMs, speech processing, vector memory, and full-stack web development.

---

## ✨ Features

### 🤖 Multi-Agent Intelligence
A Commander agent analyses every input and routes it to the most capable specialist:

| Agent | Role | Capability |
|-------|------|------------|
| **Commander** | Core routing + tool use | Handles tool calls, orchestrates all agents |
| **Researcher** | Web intelligence | Live search via DuckDuckGo, summarisation |
| **Writer** | Document generation | PDF, DOCX, TXT creation and download |
| **Coder** | Code assistance | Generation, explanation, debugging |
| **Security** | Cybersecurity analysis | Threat analysis, CVE lookup, security advice |
| **Finance (Kronos)** | Financial AI | Stock analysis, market predictions |

### 🎙️ Voice I/O
- **Wake word detection** — say *"Hey Jarvis"* to activate hands-free
- **Whisper STT** — OpenAI Whisper (local) for accurate speech-to-text
- **Auto-stop silence detection** — stops recording automatically after speech ends
- **Piper TTS** — fast, natural-sounding text-to-speech, fully offline

### 🧠 Persistent Memory
- **ChromaDB** vector store for semantic long-term memory
- Relevant past conversations are automatically recalled and injected as context
- **SQLite** chat history with full session management (rename, delete, search)

### 🛠️ Tools & Integrations
- **Spotify control** — play songs, artists, moods, skip, pause via natural language
- **Weather** — real-time forecasts via `wttr.in`
- **Screen vision** — LLaVA multimodal model analyses your screen on demand
- **File upload** — attach PDFs, images, and text files for analysis
- **File generation** — create and download PDFs, Word documents, and text files
- **Web search** — DuckDuckGo search with live news feed panel
- **System stats** — live CPU, RAM, disk, and network monitoring

### 🖥️ Iron Man-Inspired UI
- Fully custom HTML/CSS/JS frontend — no frameworks
- Arc reactor orb with orbital animations and state-aware pulse effects
- Real-time system stats with animated fill bars
- Live agent status panel showing which agent handled each request
- Particle background, scanline overlay, corner brackets
- Persistent chat sidebar with search and session management

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                        │
│                      server.py                           │
└──────────┬──────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│                  brain/llm.py                            │
│           LLM Router + Tool Call Parser                  │
│         (Ollama → LLaMA 3.1 8B local)                   │
└──────────┬──────────────────────────────────────────────┘
           │
           ▼ route()
┌──────────────────────────────────────────────────────────┐
│              agents/commander.py                          │
│    Classifies intent → selects specialist agent          │
└───┬──────┬────────┬──────────┬───────────┬──────────────┘
    │      │        │          │           │
    ▼      ▼        ▼          ▼           ▼
researcher writer  coder   security    finance
(ddgs)   (docx/   (code    (analysis)  (Kronos)
          pdf)    exec)
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│                   tools/                                  │
│  executor · spotify · weather · file_writer              │
└─────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│               memory/ + database.py                       │
│         ChromaDB (vector)  +  SQLite (history)           │
└─────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│               voice/                                      │
│     Whisper STT  ·  Piper TTS  ·  openwakeword           │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
jarvis/
├── server.py              # FastAPI app — all endpoints
├── database.py            # SQLite chat history
├── brain/
│   └── llm.py             # LLM routing, tool parsing, agent dispatch
├── agents/
│   ├── commander.py       # Intent classification + routing
│   ├── researcher.py      # Web search agent
│   ├── writer.py          # Document generation agent
│   ├── coder.py           # Code generation + execution
│   ├── security.py        # Cybersecurity analysis agent
│   └── finance.py         # Kronos finance agent
├── tools/
│   ├── executor.py        # Tool dispatcher
│   ├── spotify.py         # Spotify integration (spotipy)
│   ├── weather.py         # Weather via wttr.in
│   └── file_writer.py     # PDF / DOCX / TXT generation
├── voice/
│   ├── listener.py        # Whisper STT
│   └── wakeword.py        # openwakeword detection
├── vision/
│   └── screen.py          # Screenshot + LLaVA analysis
├── memory/
│   └── remember.py        # ChromaDB vector memory
└── static/
    └── index.html         # Full frontend UI
```

---

## ⚙️ Setup

### Prerequisites
- Windows 10/11 with NVIDIA GPU (tested on RTX series)
- Python 3.11+
- [Ollama](https://ollama.com/download) installed and running
- [Piper TTS](https://github.com/rhasspy/piper) with `en_US-lessac-medium` voice model
- [FFmpeg](https://ffmpeg.org/download.html) on PATH
- Spotify Premium account (for Spotify features)

### Installation

```powershell
# 1. Clone the repo
git clone https://github.com/Drild/A.E.G.I.S.git
cd A.E.G.I.S

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Pull required Ollama models
ollama pull llama3.1:8b
ollama pull llava

# 5. Start Ollama (in a separate terminal)
ollama serve

# 6. Start A.E.G.I.S
uvicorn server:app --reload
```

Then open `http://127.0.0.1:8000` in your browser.

### Spotify Setup
Create a `.env` file in the project root:
```env
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
```
Get credentials from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|------------|
| **LLM** | Ollama · LLaMA 3.1 8B · LLaVA |
| **Backend** | Python · FastAPI · Uvicorn |
| **Speech** | OpenAI Whisper (local) · Piper TTS · openwakeword |
| **Memory** | ChromaDB · SQLite |
| **Tools** | spotipy · psutil · ddgs · wttr.in · PyMuPDF · python-docx |
| **Frontend** | Vanilla HTML/CSS/JS (no frameworks) |
| **Hardware** | NVIDIA GPU (CUDA accelerated) |

---

## 🔒 Privacy

Everything runs locally. No data is sent to any external server except:
- `wttr.in` for weather queries
- `duckduckgo.com` for web searches (when explicitly requested)
- Spotify API for music control (requires your own credentials)

Your conversations, files, and voice input never leave your machine.

---

## 👤 Author

**Drilden** — First-year BSc Computer Science (Cybersecurity) student at Newcastle University.

[![GitHub](https://img.shields.io/badge/GitHub-Drild-00d4ff?style=flat-square&logo=github&labelColor=020408)](https://github.com/Drild)

---

<div align="center">
  <sub>Built with Python · Powered by local LLMs · Inspired by Iron Man</sub>
</div>