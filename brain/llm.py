import ollama
import json
from memory.remember import search_memory
from agents.commander import route
from agents.researcher import research
from agents.writer import write
from agents.coder import code
from agents.security import security_analysis

SYSTEM_PROMPT = """
You are Jarvis, a highly capable personal AI assistant.
You are concise, intelligent, and helpful.

CRITICAL RULES:
- If the user asks to save, generate, create, write, or download ANY file (PDF, Word doc, text) you MUST use the appropriate save tool. Never just reply with the content — always save it.
- If the user references a previously uploaded file, it will appear in their message as [ATTACHED FILE: filename]. Remember its contents for the rest of the conversation.
- Never tell the user you don't have access to a file they uploaded — it will always be included in their message.
- "play [song/artist]" ALWAYS means use the play_song tool. Never use current_track for play commands.
- If the user says ONLY "play [song]", ALWAYS use play_song immediately.
- If the previous message was about a song and the user says "play [song]", they want to change the song.

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
- save_txt: Saves a text file. Argument = ONLY the raw content, no preamble.
- save_docx: Saves a Word document. Argument = ONLY the raw content, no preamble.
- save_pdf: Saves a PDF. Argument = ONLY the raw content, no preamble.
- none: No tool needed, just reply normally.

You must ALWAYS respond in this exact JSON format:
{
  "tool": "tool_name_or_none",
  "argument": "argument_if_needed_or_empty",
  "reply": "your spoken response to the user"
}

When saving files, the argument must contain ONLY the raw content to save. No preamble, no explanations. Just the content itself.
No extra text. Only valid JSON.
"""

conversation_history = []

def chat(user_message: str) -> tuple[str, str, str, str]:
    memories = search_memory(user_message)
    memory_block = f"\nRelevant past conversations:\n{memories}\n" if memories else ""

    # Route to specialist agent if needed
    agent = route(user_message)

    if agent == "researcher":
        reply = research(user_message)
        return "none", "", reply, "researcher"

    elif agent == "writer":
        reply = write(user_message)
        return "none", "", reply, "writer"

    elif agent == "coder":
        reply = code(user_message)
        return "none", "", reply, "coder"

    elif agent == "coder_run":
        from agents.coder import run_code
        reply = run_code(user_message)
        return "none", "", reply, "coder_run"

    elif agent == "security":
        reply = security_analysis(user_message)
        return "none", "", reply, "security"

    # Default: Jarvis handles it with tool calling
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    response = ollama.chat(
        model="llama3.1:8b",
        options={"temperature": 0.1},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT + memory_block}
        ] + conversation_history
    )

    raw = response["message"]["content"].strip()

    conversation_history.append({
        "role": "assistant",
        "content": raw
    })

    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        parsed = json.loads(raw[start:end])
        tool = parsed.get("tool", "none")
        argument = parsed.get("argument", "")
        reply = parsed.get("reply", raw)
    except (ValueError, json.JSONDecodeError):
        tool = "none"
        argument = ""
        reply = raw

    return tool, argument, reply, "jarvis"