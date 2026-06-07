import ollama
import json

COMMANDER_PROMPT = """
You are the Commander Agent for A.E.G.I.S. Your job is to read the user's message and decide which specialist agent should handle it.

PRIORITY RULES — check these FIRST before routing:
- If the message contains "weather", "temperature", "raining", "forecast", "hot", "cold outside" → route to "aegis" (has weather tool)
- If the message contains "play", "pause", "skip", "spotify", "song", "music" → route to "aegis"
- If the message contains "open", "launch", "time", "note", "screenshot", "screen", "save", "pdf", "download" → route to "aegis"

Agents available:
- researcher: Questions requiring current information, news, facts, "what is", "how does", "latest", "who is", "search for" — NOT weather or music
- writer: Creating documents, emails, essays, CVs, reports, summaries, rewrites, creative writing
- coder: Writing code, explaining code, debugging, programming questions
- coder_run: Execute code and see output — "calculate", "compute", "run", "what is the result of"
- security: Cybersecurity questions, vulnerabilities, CTF challenges, network security
- aegis: General chat, weather, music, tools, file operations, screen analysis, time
- finance: Stock market analysis, price predictions, market trends. Use for "analyse [stock]", "stock price", "forecast [company]", "bullish", "bearish", "predict", "market"

Respond ONLY with valid JSON:
{
  "agent": "agent_name",
  "reason": "one line explanation"
}
"""

def route(user_message: str) -> str:
    msg = user_message.lower()

    # Hard-coded priority rules — never let these go to other agents
    weather_words = ["weather", "temperature", "raining", "forecast", "hot outside", "cold outside", "sunny", "cloudy", "wind"]
    music_words = ["play ", "pause music", "skip track", "next song", "previous song", "what's playing", "spotify"]
    tool_words = ["open ", "launch ", "what time", "write a note", "screenshot", "my screen", "save as pdf", "save as doc", "download file"]
    finance_words = ["stock", "share price", "market", "bullish", "bearish", "predict", "forecast", "analyse", "analyze", "nasdaq", "nyse", "crypto", "bitcoin", "ethereum"]


    if any(w in msg for w in weather_words):
        return "aegis"
    if any(w in msg for w in music_words):
        return "aegis"
    if any(w in msg for w in tool_words):
        return "aegis"
    if any(w in msg for w in finance_words):
        return "finance"



    # Let LLM decide for everything else
    try:
        response = ollama.chat(
            model="llama3.1:8b",
            options={"temperature": 0.0},
            messages=[
                {"role": "system", "content": COMMANDER_PROMPT},
                {"role": "user", "content": user_message}
            ]
        )
        raw = response["message"]["content"].strip()
        start = raw.index("{")
        end = raw.rindex("}") + 1
        parsed = json.loads(raw[start:end])
        return parsed.get("agent", "aegis")
    except Exception:
        return "aegis"