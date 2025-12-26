import os
import datetime
from openai import OpenAI

class AgentState:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-5-nano"

        self.history = []
        self.level_estimate = "unknown"
        self.daily_plan = ""
        self.current_quiz_questions = []

    # ---------- Core LLM Call ----------
    def call_llm(self, messages):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"LLM error: {e}"

    # ---------- Central Brain ----------
    def assess_level_and_plan(self, user_input=None, mode="chat"):
        system_prompt = (
            "You are a professional German C1 tutor.\n"
            "You chat naturally, correct mistakes gently, explain briefly, "
            "and continuously assess the student's level in the background.\n"
            "You adapt future lessons and quizzes based on performance."
        )

        # --- Chat Mode ---
        if mode == "chat":
            if user_input:
                self.history.append({"role": "user", "content": user_input})

            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(self.history[-10:])  # keep context small

            assistant_reply = self.call_llm(messages)

            self.history.append({"role": "assistant", "content": assistant_reply})
            return assistant_reply

        # --- Lesson Mode ---
        if mode == "lesson":
            today = datetime.datetime.now().strftime("%A (%d %B)")
            lesson_prompt = (
                f"Create a concise but high-quality German C1 lesson for {today}.\n"
                "Include:\n"
                "- 1 grammar focus\n"
                "- 1 vocabulary theme\n"
                "- 2 example sentences\n"
                "- 1 short exercise"
            )

            return self.call_llm([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": lesson_prompt}
            ])

        # --- Quiz Mode ---
        if mode == "quiz":
            quiz_prompt = (
                "Create a German C1 daily quiz with EXACTLY 5 questions:\n"
                "1. Grammar correction\n"
                "2. Vocabulary usage\n"
                "3. Sentence transformation\n"
                "4. Short paragraph writing (3–4 lines)\n"
                "5. Comprehension or opinion question\n\n"
                "Return ONLY the questions, numbered 1–5, each on a new line."
            )

            quiz_text = self.call_llm([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": quiz_prompt}
            ])

            questions = [
                q.strip() for q in quiz_text.split("\n")
                if q.strip() and q.strip()[0].isdigit()
            ]

            self.current_quiz_questions = questions[:5]
            return self.current_quiz_questions

        return "Invalid mode."
