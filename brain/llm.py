import ollama
import json
from memory.remember import search_memory
from agents.commander import route
from agents.researcher import research
from agents.writer import write
from agents.coder import code
from agents.security import security_analysis
from agents.finance import analyse_stock

SYSTEM_PROMPT = """
You are A.E.G.I.S (Autonomous Expert Guardian Intelligence System), a highly capable personal AI assistant.
You are concise, intelligent, and helpful.

CRITICAL RULES:
- If the user asks to save, generate, create, write, or download ANY file (PDF, Word doc, text) you MUST use the appropriate save tool. Never just reply with the content — always save it.
- If the user references a previously uploaded file, it will appear in their message as [ATTACHED FILE: filename]. Remember its contents for the rest of the conversation.
- Never tell the user you don't have access to a file they uploaded — it will always be included in their message.
- "play [song/artist]" ALWAYS means use the play_song tool. Never use current_track for play commands.
- If the user says ONLY "play [song]", ALWAYS use play_song immediately.
- NEVER use search_web for weather questions. ALWAYS use get_weather or get_weather_detailed tools instead.
- When saving files, the argument must contain ONLY the raw content to save. No preamble, no explanations.

You have access to the following tools:
- open_app: Opens an application.
- search_web: Searches Google.
- get_time: Returns current time/date.
- write_note: Saves a quick note.
- play_song: Plays a song on Spotify.
- pause_music: Pauses Spotify playback.
- next_track: Skips to next track.
- previous_track: Goes to previous track.
- current_track: Returns what's currently playing.
- analyse_screen: Takes a screenshot and analyses it.
- get_weather: Gets current weather. Argument = city name.
- get_weather_detailed: Gets detailed weather info.
- save_txt: Saves a text file. Argument = ONLY the raw content.
- save_docx: Saves a Word document. Argument = ONLY the raw content.
- save_pdf: Saves a PDF. Argument = ONLY the raw content.
- none: No tool needed, just reply normally.

You must ALWAYS respond with a SINGLE JSON object and nothing else:
{"tool": "tool_name_or_none", "argument": "argument_if_needed_or_empty", "reply": "your spoken response to the user"}

No extra text. No multiple JSON objects. Only ONE valid JSON object per response.
"""

# Separate conversation histories per agent — store only clean text, not raw JSON
conversation_histories = {
    "aegis": [],
    "researcher": [],
    "writer": [],
    "coder": [],
    "security": [],
    "finance": [],
}

last_agent = "aegis"

def get_agent_context(agent: str, user_message: str) -> str:
    history = conversation_histories.get(agent, [])
    if not history:
        return ""
    recent = history[-6:]
    context = "\n".join([f"{m['role'].upper()}: {m['content'][:200]}" for m in recent])
    return f"\nPrevious conversation context:\n{context}\n"

def add_to_history(agent: str, role: str, content: str):
    if agent not in conversation_histories:
        conversation_histories[agent] = []
    conversation_histories[agent].append({"role": role, "content": content})
    if len(conversation_histories[agent]) > 20:
        conversation_histories[agent] = conversation_histories[agent][-20:]

def parse_llm_response(raw: str) -> tuple[str, str, str]:
    """
    Extract the FIRST valid JSON object from raw LLM output.
    Returns (tool, argument, reply).
    Falls back gracefully if parsing fails.
    """
    raw = raw.strip()

    # Find the first complete JSON object only
    depth = 0
    start = None
    for i, ch in enumerate(raw):
        if ch == "{":
            if start is None:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    parsed = json.loads(raw[start:i+1])
                    tool     = parsed.get("tool", "none") or "none"
                    argument = parsed.get("argument", "") or ""
                    reply    = parsed.get("reply", "").strip()
                    # If reply is empty, produce a fallback
                    if not reply:
                        if tool != "none":
                            reply = f"Running {tool}..."
                        else:
                            reply = "I'm on it."
                    return tool, argument, reply
                except json.JSONDecodeError:
                    # Reset and keep searching
                    start = None
                    depth = 0
                break

    # No JSON found — treat entire response as a plain reply
    return "none", "", raw if raw else "I'm ready."

def chat(user_message: str) -> tuple[str, str, str, str]:
    global last_agent
    memories = search_memory(user_message)
    memory_block = f"\nRelevant past conversations:\n{memories}\n" if memories else ""

    agent = route(user_message)

    followup_phrases = [
        "more", "tell me more", "can i get", "give me more", "and also",
        "what about", "how about", "continue", "go on", "yes", "sure",
        "ok", "okay", "sounds good", "great", "thanks", "explain more",
        "elaborate", "expand", "another", "5 more", "10 more"
    ]
    msg_lower = user_message.lower().strip()
    is_followup = (
        len(user_message.split()) <= 6 or
        any(phrase in msg_lower for phrase in followup_phrases)
    )

    if is_followup and last_agent != "aegis":
        agent = last_agent

    last_agent = agent
    add_to_history(agent, "user", user_message)
    context = get_agent_context(agent, user_message)
    full_message = f"{context}{user_message}" if context else user_message

    if agent == "researcher":
        reply = research(full_message)
        add_to_history(agent, "assistant", reply)
        return "none", "", reply, "researcher"

    elif agent == "writer":
        reply = write(full_message)
        add_to_history(agent, "assistant", reply)
        return "none", "", reply, "writer"

    elif agent == "coder":
        reply = code(full_message)
        add_to_history(agent, "assistant", reply)
        return "none", "", reply, "coder"

    elif agent == "coder_run":
        from agents.coder import run_code
        reply = run_code(full_message)
        add_to_history(agent, "assistant", reply)
        return "none", "", reply, "coder_run"

    elif agent == "security":
        reply = security_analysis(full_message)
        add_to_history(agent, "assistant", reply)
        return "none", "", reply, "security"

    elif agent == "finance":
        reply = analyse_stock(full_message)
        add_to_history(agent, "assistant", reply)
        return "none", "", reply, "finance"

    # Default: A.E.G.I.S with tool calling
    # Build messages for Ollama using clean human-readable history only
    ollama_messages = [{"role": "system", "content": SYSTEM_PROMPT + memory_block}]
    for msg in conversation_histories["aegis"][-18:]:  # last 18 to leave room
        ollama_messages.append({"role": msg["role"], "content": msg["content"]})
    # Add current user message
    ollama_messages.append({"role": "user", "content": user_message})

    response = ollama.chat(
        model="llama3.1:8b",
        options={"temperature": 0.1},
        messages=ollama_messages
    )

    raw = response["message"]["content"].strip()

    tool, argument, reply = parse_llm_response(raw)

    # Store only the clean reply in history (not raw JSON)
    add_to_history("aegis", "user", user_message)
    add_to_history("aegis", "assistant", reply)

    # Trim
    if len(conversation_histories["aegis"]) > 20:
        conversation_histories["aegis"] = conversation_histories["aegis"][-20:]

    return tool, argument, reply, "aegis"