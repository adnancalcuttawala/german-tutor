import openai
import os
from datetime import datetime
import json

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class AgentState:
    def __init__(self):
        # Store chat history per day
        self.chat_history = []
        self.daily_plan = {}
        self.quiz_history = []

    def call_llm(self, user_message, system_prompt="You are a German C1 tutor."):
        """
        Call GPT-5-nano for a chat response
        """
        messages = [{"role": "system", "content": system_prompt}]
        # Include previous conversation for context
        for entry in self.chat_history[-10:]:  # last 10 messages
            messages.append(entry)
        messages.append({"role": "user", "content": user_message})

        try:
            response = openai.chat.completions.create(
                model="gpt-5-nano",
                messages=messages
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"LLM error: {e}"

        # Store in chat history
        self.chat_history.append({"role": "user", "content": user_message})
        self.chat_history.append({"role": "assistant", "content": reply})

        return reply

    def assess_level_and_plan(self, user_input=None, mode="chat"):
        """
        mode: "chat", "lesson", "quiz"
        """
        today = datetime.now().strftime("%Y-%m-%d")
        if mode == "chat" and user_input:
            return self.call_llm(user_input)
        elif mode == "lesson":
            prompt = "Create a daily German C1 lesson for the user based on previous chat history."
            lesson = self.call_llm(prompt)
            self.daily_plan[today] = {"lesson": lesson}
            return lesson
        elif mode == "quiz":
            prompt = "Create a small quiz based on today's lesson."
            quiz = self.call_llm(prompt)
            self.daily_plan[today]["quiz"] = quiz
            self.quiz_history.append({today: quiz})
            return quiz
        else:
            return "Invalid mode."
