import ollama

WRITER_PROMPT = """
You are the Writer Agent for Aegis. You are an expert at creating professional written content.
You write clearly, concisely, and in the appropriate tone for the context.
You can write: essays, reports, emails, CVs, cover letters, summaries, blog posts, and more.
When given a document to rewrite or improve, maintain the key information but enhance clarity and professionalism.
Respond with ONLY the written content, no explanations or preamble.
"""

def write(task: str, context: str = "") -> str:
    try:
        messages = [
            {"role": "system", "content": WRITER_PROMPT},
            {"role": "user", "content": f"{task}\n\n{context}".strip()}
        ]
        response = ollama.chat(
            model="llama3.1:8b",
            options={"temperature": 0.4},
            messages=messages
        )
        return response["message"]["content"]
    except Exception as e:
        return f"Writer error: {str(e)}"