import gradio as gr
from agent_state import AgentState

agent = AgentState()

def chat_fn(msg):
    return agent.assess_level_and_plan(user_input=msg, mode="chat")

def lesson_fn():
    return agent.assess_level_and_plan(mode="lesson")

def quiz_fn():
    return agent.assess_level_and_plan(mode="quiz")

with gr.Blocks() as demo:
    gr.Markdown("# German C1 Tutor 🤖🇩🇪")

    with gr.Tab("Chat"):
        chat_input = gr.Textbox(label="Your message", lines=3, placeholder="Schreibe hier...", interactive=True)
        chat_output = gr.Textbox(label="Tutor response", lines=10)
        chat_button = gr.Button("Send")
        chat_button.click(chat_fn, inputs=chat_input, outputs=chat_output)

    with gr.Tab("Daily Lesson"):
        lesson_button = gr.Button("Generate Lesson")
        lesson_output = gr.Textbox(label="Today's Lesson", lines=15)
        lesson_button.click(lesson_fn, inputs=[], outputs=lesson_output)

    with gr.Tab("Daily Quiz"):
        quiz_button = gr.Button("Generate Quiz")
        quiz_output = gr.Textbox(label="Quiz", lines=10)
        quiz_button.click(quiz_fn, inputs=[], outputs=quiz_output)

demo.launch(share=True, server_name="0.0.0.0", server_port=7860)
