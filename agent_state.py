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

        # Model configuration
        self.model = "meta-llama/Llama-3.1-8B-Instruct"  # Chat-compatible model
        self.api_token = os.getenv("HF_API_TOKEN")      # Hugging Face token
        self.headers = {"Authorization": f"Bearer {self.api_token}"}

    def save_memory(self):
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def call_llm(self, messages, max_tokens=500):
        """
        messages: List of dicts with role/content, e.g.
        [{"role": "system", "content": "You are a German C1 tutor."},
         {"role": "user", "content": "Hallo!"}]
        """
        url = f"https://api-inference.huggingface.co/v1/models/{self.model}/chat-completion"
        payload = {"inputs": messages, "parameters": {"max_new_tokens": max_tokens}}

        try:
            r = requests.post(url, headers=self.headers, json=payload, timeout=60)
            data = r.json()
            if "error" in data:
                return f"LLM error: {data['error']}"
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            return f"Unexpected LLM response: {data}"
        except Exception as e:
            return f"LLM request failed: {e}"

    def assess_level_and_plan(self, user_input=None, mode="chat"):
        today = str(datetime.now(self.tz).date())
        if today not in self.state:
            self.state[today] = {"chat": [], "lesson": "", "quiz": ""}

        if mode == "chat" and user_input:
            messages = [
                {"role": "system", "content": "Du bist ein freundlicher Deutschlehrer auf C1 Niveau. "
                                               "Gib Feedback, neue Wörter, Grammatiktipps und reagiere freundlich."},
                {"role": "user", "content": user_input}
            ]
            response = self.call_llm(messages)
            self.state[today]["chat"].append({"user": user_input, "agent": response})
            self.save_memory()
            return response

        elif mode == "lesson":
            messages = [
                {"role": "system", "content": "Du bist ein Deutschlehrer auf C1 Niveau."},
                {"role": "user", "content": "Erstelle eine vollständige Lektion für den heutigen Tag basierend auf dem bisherigen Verlauf."}
            ]
            lesson = self.call_llm(messages)
            self.state[today]["lesson"] = lesson
            self.save_memory()
            return lesson

        elif mode == "quiz":
            chat_history = self.state[today]["chat"]
            if not chat_history:
                return "Noch kein Chatverlauf, Quiz kann nicht erstellt werden."
            chat_text = " ".join([c["user"] + " " + c["agent"] for c in chat_history])
            messages = [
                {"role": "system", "content": "Du bist ein Deutschlehrer auf C1 Niveau."},
                {"role": "user", "content": f"Erstelle 3 Quizfragen basierend auf folgendem Chatverlauf:\n{chat_text}"}
            ]
            quiz = self.call_llm(messages)
            self.state[today]["quiz"] = quiz
            self.save_memory()
            return quiz
