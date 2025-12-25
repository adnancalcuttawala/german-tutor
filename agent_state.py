import json
import os
import requests
from datetime import datetime
import pytz

class AgentState:
    def __init__(self, memory_file="memory.json"):
        self.memory_file = memory_file
        if os.path.exists(memory_file):
            with open(memory_file, "r", encoding="utf-8") as f:
                self.state = json.load(f)
        else:
            self.state = {}
        self.tz = pytz.timezone("Europe/Berlin")

        # LLM config
        self.model = "meta-llama/Llama-3.1-8B-Instruct"
        self.api_token = os.getenv("HF_API_TOKEN")  # Store your Hugging Face token in environment variable
        self.headers = {"Authorization": f"Bearer {self.api_token}"}

    def save_memory(self):
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def call_llm(self, prompt, max_tokens=500):
        url = f"https://api-inference.huggingface.co/models/{self.model}"
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_tokens}}
        r = requests.post(url, headers=self.headers, json=payload)
        try:
            return r.json()[0]["generated_text"]
        except Exception as e:
            return f"LLM error: {e}"

    def assess_level_and_plan(self, user_input=None, mode="chat"):
        today = str(datetime.now(self.tz).date())
        if today not in self.state:
            self.state[today] = {"chat": [], "lesson": "", "quiz": ""}

        if mode == "chat" and user_input:
            # Friendly tutor prompt
            prompt = f"""
Du bist ein freundlicher Deutschlehrer auf C1 Niveau.
Der Benutzer schreibt: "{user_input}"

1. Korrigiere kleine Fehler sanft, falls vorhanden.
2. Gib neue Wörter oder Phrasen, die nützlich sind.
3. Schreibe eine kurze Antwort, die das Gespräch fortsetzt und den Benutzer zum Üben anregt.
"""
            response = self.call_llm(prompt)
            self.state[today]["chat"].append({"user": user_input, "agent": response})
            self.save_memory()
            return response

        elif mode == "lesson":
            prompt = "Bitte erstelle meinen täglichen Deutschunterricht auf C1 Niveau basierend auf dem bisherigen Verlauf."
            lesson = self.call_llm(prompt)
            self.state[today]["lesson"] = lesson
            self.save_memory()
            return lesson

        elif mode == "quiz":
            chat_history = self.state[today]["chat"]
            if not chat_history:
                return "No chat history to generate quiz from."
            chat_text = " ".join([c["user"] + " " + c["agent"] for c in chat_history])
            prompt = f"""
Du bist ein Deutschlehrer auf C1 Niveau. Erstelle 3 kurze Fragen basierend auf folgendem heutigen Chat:
'{chat_text}'
Gib die Antworten ebenfalls an, klar markiert.
"""
            quiz = self.call_llm(prompt)
            self.state[today]["quiz"] = quiz
            self.save_memory()
            return quiz
