import os
import subprocess
import webbrowser
from tools.weather import get_weather, get_weather_detailed
from datetime import datetime
from tools.spotify import play_song, pause_music, next_track, previous_track, current_track
from vision.screen import analyse_screen
from tools.file_writer import save_text_file, save_docx, save_pdf

def open_app(app: str) -> str:
    apps = {
        "spotify": "spotify",
        "notepad": "notepad",
        "calculator": "calc",
        "browser": "start chrome",
        "chrome": "start chrome",
        "firefox": "start firefox",
        "explorer": "explorer",
        "discord": "discord",
        "vscode": "code",
    }
    app_lower = app.lower()
    for key, command in apps.items():
        if key in app_lower:
            os.system(command)
            return f"Opening {key}."
    os.system(f"start {app}")
    return f"Trying to open {app}."

def search_web(query: str) -> str:
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Searching for '{query}'."

def get_time() -> str:
    now = datetime.now()
    return f"It's {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d')}."

def write_note(content: str) -> str:
    path = os.path.join(os.path.expanduser("~"), "aegis_notes.txt")
    with open(path, "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {content}\n")
    return "Note saved."

def execute_tool(tool: str, argument: str = "") -> str:
    if tool == "open_app":
        return open_app(argument)
    elif tool == "search_web":
        return search_web(argument)
    elif tool == "get_time":
        return get_time()
    elif tool == "write_note":
        return write_note(argument)
    elif tool == "play_song":
        return play_song(argument)
    elif tool == "pause_music":
        return pause_music()
    elif tool == "next_track":
        return next_track()
    elif tool == "previous_track":
        return previous_track()
    elif tool == "current_track":
        return current_track()
    elif tool == "analyse_screen":
        return analyse_screen(argument)
    elif tool == "save_txt":
        path = save_text_file(argument)
        return f"Saved to {path}"
    elif tool == "save_docx":
        path = save_docx(argument)
        return f"Saved to {path}"
    elif tool == "save_pdf":
        path = save_pdf(argument)
        return f"Saved to {path}"
    elif tool == "get_weather":
        return get_weather(argument)
    elif tool == "get_weather_detailed":
        return get_weather_detailed(argument)
    else:
        return ""