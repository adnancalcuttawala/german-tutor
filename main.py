import os
import gradio as gr
from agent_state import AgentState
from datetime import datetime
import pytz
import schedule
import threading
import time

# Initialize agent
agent = AgentState()

# German timezone
GERMAN_TZ = pytz.timezone("Europe/Berlin")

# --- Automated tasks ---
def morning_lesson():
    today = datetime.now(GERMAN_TZ).date()
    if agent.state.get("last_lesson_date") == str(today):
        print("Morning lesson already generated today.")
        return

    prompt = "Bitte erstelle meinen täglichen Deutschunterricht auf C1 Niveau."
    lesson = agent.assess_level_and_plan(prompt)
    agent.state["last_lesson_date"] = str(today)
    agent.save_memory()
    
    # Append lesson to memory so Gradio can access it
    agent.state.setdefault("today_lesson", lesson)
    print(f"\n--- Morning Lesson ({today}) ---\n{lesson}\n----------------------------\n")

def night_quiz():
    today = datetime.now(GERMAN_TZ).date()
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
    
    # Store quiz so Gradio can access it
    agent.state.setdefault("today_quiz", quiz)
    print(f"\n--- End-of-Day Quiz ({today}) ---\n{quiz}\n----------------------------\n")

# --- Schedule tasks ---
schedule.every().day.at("08:00").do(morning_lesson)
schedule.every().day.at("21:00").do(night_quiz)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start scheduler in background thread
threading.Thread(target=run_schedule, daemon=True).start()

# --- Gradio functions ---
def chat_interface(user_input):
    response = agent.assess_level_and_plan(user_input)
    return response

def get_today_lesson():
    return agent.state.get("today_lesson", "Morning lesson not yet generated.")

def get_today_quiz():
    return agent.state.get("today_quiz", "End-of-day quiz not yet generated.")

# --- Gradio UI ---
with gr.Blocks() as demo:
    gr.Markdown("<h1 style='text-align: center'>Agentic German Tutor (C1)</h1>")

    chatbot = gr.Chatbot(elem_id="chatbot")

    with gr.Row():
        user_message = gr.Textbox(
            label="Your Message",
            placeholder="Type your message here...",
            lines=5,
            elem_id="user_input"
        )
        submit_btn = gr.Button("Send")

    output_box = gr.Textbox(
        label="Agent Response",
        placeholder="Agent's response will appear here...",
        lines=15,
        interactive=False
    )

    submit_btn.click(lambda msg: chat_interface(msg), inputs=user_message, outputs=output_box)
    user_message.submit(lambda msg: chat_interface(msg), inputs=user_message, outputs=output_box)

    # Buttons to view automatic lessons and quizzes
    lesson_btn = gr.Button("View Today's Lesson")
    lesson_output = gr.Textbox(label="Today's Lesson", lines=15, interactive=False)
    lesson_btn.click(get_today_lesson, inputs=None, outputs=lesson_output)

    quiz_btn = gr.Button("View End-of-Day Quiz")
    quiz_output = gr.Textbox(label="Today's Quiz", lines=15, interactive=False)
    quiz_btn.click(get_today_quiz, inputs=None, outputs=quiz_output)

# Launch Gradio
demo.launch(server_name="0.0.0.0", server_port=7860)
