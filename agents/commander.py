import ollama
import json

COMMANDER_PROMPT = """
You are the Commander Agent for Aegis. Your job is to read the user's message and decide which specialist agent should handle it.

Agents available:
- researcher: Questions requiring current information, news, facts, web search, "what is", "how does", "latest", "search for"
- writer: Creating documents, emails, essays, CVs, reports, summaries, rewrites, creative writing
- coder: Writing code, explaining code, debugging, programming questions — when user wants to SEE the code
- coder_run: When user wants to EXECUTE code and see output — "calculate", "compute", "run", "what is the result of", "how many", mathematical computations
- security: Cybersecurity questions, vulnerabilities, CTF challenges, network security, hacking concepts
- aegis: Everything else — general chat, tool commands (spotify, open app, time, notes, screen analysis)

Respond ONLY with valid JSON in this exact format:
{
  "agent": "agent_name",
  "reason": "one line explanation"
}
"""

def route(user_message: str) -> str:
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