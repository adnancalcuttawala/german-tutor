import gradio as gr
from agent_state import AgentState
from datetime import datetime
import pytz
import schedule
import threading
import time

agent = AgentState()
GERMAN_TZ = pytz.timezone("Europe/Berlin")

# --- Scheduled tasks ---
def daily_lesson():
    print("\nGenerating morning lesson...")
    lesson = agent.assess_level_and_plan(mode="lesson")
    print(f"Today's Lesson:\n{lesson}\n")

def nightly_quiz():
    print("\nGenerating end-of-day quiz...")
    quiz = agent.assess_level_and_plan(mode="quiz")
    print(f"Today's Quiz:\n{quiz}\n")

schedule.every().day.at("08:00").do(daily_lesson)
schedule.every().day.at("21:00").do(nightly_quiz)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(60)

threading.Thread(target=run_schedule, daemon=True).start()

# --- Gradio functions ---
def chat_interface(user_input):
    return agent.assess_level_and_plan(user_input=user_input, mode="chat")

def view_lesson():
    today = str(datetime.now(GERMAN_TZ).date())
    return agent.state.get(today, {}).get("lesson", "Morning lesson not generated yet.")

def view_quiz():
    today = str(datetime.now(GERMAN_TZ).date())
    return agent.state.get(today, {}).get("quiz", "End-of-day quiz not generated yet.")

# --- Gradio UI ---
with gr.Blocks() as demo:
    gr.Markdown("<h1 style='text-align:center'>Agentic German Tutor (C1)</h1>")

    user_msg = gr.Textbox(label="Your Message", lines=5)
    chat_output = gr.Textbox(label="Agent Response", lines=15, interactive=False)
    send_btn = gr.Button("Send")

    lesson_btn = gr.Button("View Today's Lesson")
    lesson_box = gr.Textbox(label="Today's Lesson", lines=15, interactive=False)

    quiz_btn = gr.Button("View Today's Quiz")
    quiz_box = gr.Textbox(label="Today's Quiz", lines=15, interactive=False)

    send_btn.click(chat_interface, inputs=user_msg, outputs=chat_output)
    user_msg.submit(chat_interface, inputs=user_msg, outputs=chat_output)

    lesson_btn.click(view_lesson, inputs=None, outputs=lesson_box)
    quiz_btn.click(view_quiz, inputs=None, outputs=quiz_box)

demo.launch(server_name="0.0.0.0", server_port=7860)
