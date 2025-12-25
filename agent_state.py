import requests
import os
import json
from datetime import date

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

class AgentState:
    def __init__(self):
        self.memory_file = "memory.json"
        if os.path.exists(self.memory_file):
            self.memory = json.load(open(self.memory_file, "r", encoding="utf-8"))
        else:
            self.memory = {
                "level": "unknown",
                "daily_plan": {},
                "history": []
            }

    def call_llm(self, prompt):
        headers = {
            "Authorization": f"Bearer {HF_API_TOKEN}"
        }
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 400}
        }
        r = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_MODEL}",
            headers=headers,
            json=payload,
            timeout=60
        )
        return r.json()[0]["generated_text"]

    def assess_level_and_plan(self, user_input):
        prompt = f"""
You are a C1 German teacher.
User message:
{user_input}

1. Assess the user's CEFR level.
2. Create a daily plan with:
- Vocabulary (5 items)
- Grammar (2 topics)
- Phrase practice
Return JSON.
"""
        response = self.call_llm(prompt)
        self.memory["history"].append(user_input)
        json.dump(self.memory, open(self.memory_file, "w", encoding="utf-8"), indent=2)
        return response
