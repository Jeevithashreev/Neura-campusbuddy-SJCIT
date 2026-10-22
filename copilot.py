"""Admin AI copilot: sends the live building data to Gemini and returns an answer.
The API key is read from the .env file and is never written in code."""
import json
import os
import urllib.error
import urllib.request


def _load_env():
    try:
        with open(".env", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except FileNotFoundError:
        pass


_load_env()
MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")


def ask(question, state):
    key = os.getenv("GEMINI_API_KEY")
    if not key or key == "paste-your-key-here":
        return "The copilot has no API key yet. Put GEMINI_API_KEY in the .env file and restart the server."

    prompt = (
        "You are the energy copilot for SJCIT campus admins. "
        "Answer only from the live data below. Keep it short and clear. "
        "Energy savings are simulated estimates (assumed 420 W per building), so say 'estimated'. "
        "If the data cannot answer the question, say so.\n\n"
        f"Live data (JSON):\n{json.dumps(state)}\n\n"
        f"Admin question: {question}"
    )
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=body,
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        return f"Gemini returned an error ({e.code}). Check the key and the model name."
    except Exception as e:
        return f"Could not reach Gemini: {e}"