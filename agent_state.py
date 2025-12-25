import os
import json
from datetime import date
import requests

class AgentState:
    def __init__(self):
        self.memory_file = "memory.json"
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
        """
        Calls Hugging Face router using OpenAI-compatible chat API
        with meta-llama/Llama-3.1-8B-Instruct.
        """
        try:
            response = requests.post(
                "https://router.huggingface.co/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "meta-llama/Llama-3.1-8B-Instruct",
                    "messages": [
                        {"role": "system", "content": "You are a helpful German tutor."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 512,
                    "temperature": 0.7
                },
                timeout=60
            )

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except Exception as e:
            return f"⚠️ LLM error: {str(e)}\nResponse: {response.text if 'response' in locals() else ''}"

    def assess_level_and_plan(self, user_input: str) -> str:
        today = str(date.today())
        self.state["history"].append(user_input)

        if self.state["last_date"] != today:
            self.state["last_date"] = today

        prompt = f"""
You are an expert German tutor.

User message:
"{user_input}"

Your tasks:
1. Estimate the user's CEFR level (A1–C2)
2. Briefly explain why
3. Create a DAILY STUDY PLAN to reach C1:
   - 5 advanced German vocabulary words with meanings
   - 2 grammar topics
   - 2 useful C1-level phrases
4. End with ONE short practice question

Respond clearly and structured.
"""
        reply = self.call_llm(prompt)
        self.save_memory()
        return reply
