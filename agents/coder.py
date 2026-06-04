import ollama
import subprocess
import tempfile
import os

CODER_PROMPT = """
You are the Coder Agent for Aegis. You are an expert Python developer.
When asked to write code, write clean, working, well-commented Python.
When asked to explain code, be clear and educational.
If asked to run code, output ONLY the Python code with no markdown, no backticks, no explanation — just raw executable Python.
You are the Coder Agent for Aegis. You are an expert Python developer.
When asked to write code, respond with ONLY a clean code block. No prose before or after.
Use this exact format:

```python
# your code here
```

Keep comments minimal and only where genuinely needed. No lengthy explanations unless specifically asked.


"""

def code(task: str) -> str:
    try:
        response = ollama.chat(
            model="llama3.1:8b",
            options={"temperature": 0.1},
            messages=[
                {"role": "system", "content": CODER_PROMPT},
                {"role": "user", "content": task}
            ]
        )
        return response["message"]["content"]
    except Exception as e:
        return f"Coder error: {str(e)}"

def run_code(task: str) -> str:
    try:
        # Generate code
        response = ollama.chat(
            model="llama3.1:8b",
            options={"temperature": 0.1},
            messages=[
                {"role": "system", "content": CODER_PROMPT + "\nOutput ONLY raw Python code, nothing else."},
                {"role": "user", "content": f"Write Python code to: {task}"}
            ]
        )
        code_str = response["message"]["content"].strip()
        
        # Strip markdown if present
        if "```" in code_str:
            lines = code_str.split("\n")
            code_str = "\n".join([
                l for l in lines 
                if not l.strip().startswith("```")
            ])

        # Run it
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code_str)
            tmp = f.name

        result = subprocess.run(
            ["python", tmp],
            capture_output=True, text=True, timeout=10
        )
        os.unlink(tmp)

        output = result.stdout or result.stderr
        return f"Code output:\n{output.strip()}" if output else "Code ran with no output."
    except subprocess.TimeoutExpired:
        return "Code timed out after 10 seconds."
    except Exception as e:
        return f"Run error: {str(e)}"