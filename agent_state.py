import os
import json
import requests
from datetime import date

class AgentState:
    def __init__(self):
        self.memory_file = "memory.json"
        self.api_url = "https://api-inference.huggingface.co/models/google/flan-t5-base"

        self.headers = {
            "Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"
        }

        self.state = self.load_memory()

    def load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "level": None,
            "history": [],
            "last_date": None
        }

    def save_memory(self):
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def call_llm(self, prompt: str) -> str:
        response = requests.post(
            self.api_url,
            headers=self.headers,
            json={"inputs": prompt},
            timeout=30
        )

        try:
            data = response.json()
        except Exception:
            return "⚠️ Failed to parse LLM response."

        if isinstance(data, list) and len(data) > 0:
            return data[0].get("generated_text", "⚠️ No text generated.")
        if isinstance(data, dict):
            if "generated_text" in data:
                return data["generated_text"]
            if "error" in data:
                return f"⚠️ Model error: {data['error']}"

        return "⚠️ LLM returned an unexpected response."

    def assess_level_and_plan(self, user_input: str) -> str:
        today = str(date.today())

        self.state["history"].append(user_input)

        if self.state["last_date"] != today:
            self.state["last_date"] = today

        prompt = f"""
You are an expert German C1 tutor.

User input:
"{user_input}"

Tasks:
1. Estimate the user's CEFR level (A1–C2)
2. Explain briefly why
3. Create a DAILY STUDY PLAN to reach C1:
   - 5 advanced vocabulary words with meaning
   - 2 grammar topics
   - 2 useful C1-level phrases
4. End with ONE short practice question.

Respond clearly and structured.
"""

        reply = self.call_llm(prompt)
        self.save_memory()
        return reply
