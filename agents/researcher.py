import ollama
from ddgs import DDGS
import time
import json

RESEARCHER_PROMPT = """
You are the Researcher Agent for A.E.G.I.S. Your job is to find accurate, up-to-date information.
You are knowledgeable about science, technology, history, current events, and more.
If given search results, synthesise them into a clear answer.
If no search results are available, answer from your own knowledge.
Be factual, clear, and concise. Respond in plain text, no JSON.
"""

def is_news_request(query: str) -> bool:
    news_words = ["news", "latest", "today", "headlines", "what's happening", "current events", "breaking"]
    return any(w in query.lower() for w in news_words)

def get_news(query: str) -> dict:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=8))
        return {"type": "news", "results": results}
    except Exception:
        return {"type": "news", "results": []}

def research(query: str) -> str:
    try:
        # Check if it's a news request
        if is_news_request(query):
            news_data = get_news(query)
            if news_data["results"]:
                return "NEWS:" + json.dumps(news_data["results"])

        context = ""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3, timelimit="m"))
            if results:
                context = "\n\n".join([f"{r['title']}: {r['body']}" for r in results])
        except Exception:
            pass

        user_content = f"Question: {query}\n\nSearch Results:\n{context}" if context else f"Answer this question using your knowledge: {query}"

        response = ollama.chat(
            model="llama3.1:8b",
            options={"temperature": 0.2, "num_predict": 300},
            messages=[
                {"role": "system", "content": RESEARCHER_PROMPT},
                {"role": "user", "content": user_content}
            ]
        )
        return response["message"]["content"]
    except Exception as e:
        return f"Research error: {str(e)}"