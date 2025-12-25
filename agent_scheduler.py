import os
import json
from datetime import datetime
import pytz
import schedule
import time
from agent_state import AgentState

# --- Initialize agent ---
agent = AgentState()

# --- German timezone ---
GERMAN_TZ = pytz.timezone("Europe/Berlin")

# --- Daily lesson ---
def morning_lesson():
    today = datetime.now(GERMAN_TZ).date()
    # Check if lesson already generated today
    if agent.state.get("last_lesson_date") == str(today):
        print("Morning lesson already generated today.")
        return

    prompt = "Bitte erstelle meinen täglichen Deutschunterricht auf C1 Niveau."
    lesson = agent.assess_level_and_plan(prompt)
    agent.state["last_lesson_date"] = str(today)
    agent.save_memory()
    
    print(f"\n--- Morning Lesson ({today}) ---\n")
    print(lesson)
    print("\n----------------------------\n")

# --- End-of-day quiz ---
def night_quiz():
    today = datetime.now(GERMAN_TZ).date()
    # Check if quiz already generated today
    if agent.state.get("last_quiz_date") == str(today):
        print("End-of-day quiz already generated today.")
        return

    last_entry = agent.state.get("history", [])
    if not last_entry:
        print("No lessons done today, skipping quiz.")
        return

    last_input = last_entry[-1]
    prompt = f"""
Du bist ein Deutschlehrer. Erstelle 3 kurze Fragen basierend auf folgendem heutigen Unterricht:
'{last_input}'
Gib die Antworten ebenfalls an, klar markiert.
"""
    quiz = agent.call_llm(prompt)
    agent.state["last_quiz_date"] = str(today)
    agent.save_memory()
    
    print(f"\n--- End-of-Day Quiz ({today}) ---\n")
    print(quiz)
    print("\n----------------------------\n")

# --- Schedule tasks ---
schedule.every().day.at("08:00").do(morning_lesson)  # 8 AM German time
schedule.every().day.at("21:00").do(night_quiz)     # 9 PM German time

print("Agentic German Tutor Scheduler running...")
print("Morning lesson: 08:00 CET/CEST, Night quiz: 21:00 CET/CEST")

# --- Keep running ---
while True:
    schedule.run_pending()
    time.sleep(60)  # check every minute
