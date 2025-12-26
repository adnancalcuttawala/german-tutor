import openai
import os
from datetime import datetime

# Read OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    raise ValueError("OpenAI API key not found in environment variable 'OPENAI_API_KEY'")

class AgentState:
    def __init__(self):
        self.chat_history = []
        self.daily_plan = {}
        self.quiz_history = []
        self.current_quiz_questions = []  # store current quiz questions

    def call_llm(self, user_message, system_prompt="You are a German C1 tutor."):
        messages = [{"role": "system", "content": system_prompt}]
        for entry in self.chat_history[-10:]:
            messages.append(entry)
        messages.append({"role": "user", "content": user_message})

        try:
            response = openai.chat.completions.create(
                model="gpt-5-nano",
                messages=messages,
                temperature=0.7,
                max_completion_tokens=300
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"LLM error: {e}"

        # Update chat history
        self.chat_history.append({"role": "user", "content": user_message})
        self.chat_history.append({"role": "assistant", "content": reply})

        return reply

    def assess_level_and_plan(self, user_input=None, mode="chat"):
        today = datetime.now().strftime("%Y-%m-%d")
        if mode == "chat" and user_input:
            return self.call_llm(user_input)
        elif mode == "lesson":
            prompt = "Create a daily German C1 lesson for the user based on previous chat history."
            lesson = self.call_llm(prompt)
            self.daily_plan[today] = {"lesson": lesson}
            return lesson
        elif mode == "quiz":
            prompt = "Create a small quiz based on today's lesson. Include multiple-choice or free-text questions."
            quiz = self.call_llm(prompt)
            questions = [q.strip() for q in quiz.split("\n") if q.strip()]
            self.current_quiz_questions = questions
            self.daily_plan[today] = self.daily_plan.get(today, {})
            self.daily_plan[today]["quiz"] = questions
            self.quiz_history.append({today: questions})
            return questions
        else:
            return "Invalid mode."
