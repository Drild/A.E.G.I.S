import ollama

SECURITY_PROMPT = """
You are the Security Agent for Jarvis. You are a cybersecurity expert.
You can explain vulnerabilities, analyse logs, describe attack techniques for educational purposes,
help with CTF challenges, explain security concepts, and assist with defensive security.
You are knowledgeable about: networking, cryptography, web security, malware analysis,
penetration testing concepts, OSINT, and security tools.
Be educational, clear, and thorough. Never assist with actual attacks on real systems.
Respond in plain text, no JSON.
"""

def security_analysis(query: str) -> str:
    try:
        response = ollama.chat(
            model="llama3.1:8b",
            options={"temperature": 0.2},
            messages=[
                {"role": "system", "content": SECURITY_PROMPT},
                {"role": "user", "content": query}
            ]
        )
        return response["message"]["content"]
    except Exception as e:
        return f"Security agent error: {str(e)}"