import gradio as gr
from agent_state import AgentState

agent = AgentState()

# ---------- Chat ----------
def chat_fn(msg):
    return agent.assess_level_and_plan(user_input=msg, mode="chat")

# ---------- Lesson ----------
def lesson_fn():
    return agent.assess_level_and_plan(mode="lesson")

# ---------- Quiz ----------
def generate_quiz():
    return agent.assess_level_and_plan(mode="quiz")

def populate_quiz_ui():
    questions = generate_quiz()

    md_questions = []
    for i, q in enumerate(questions):
        md_questions.append(f"### ❓ Question {i+1}\n{q}")

    while len(md_questions) < 5:
        md_questions.append("")

    return md_questions

def evaluate_quiz(a1, a2, a3, a4, a5):
    answers = [a1, a2, a3, a4, a5]
    evaluation_prompt = (
        "You are a German C1 examiner.\n"
        "Evaluate the following answers.\n"
        "Give:\n"
        "- Per-question feedback\n"
        "- Overall score out of 10\n"
        "- One improvement tip\n\n"
    )

    for i, q in enumerate(agent.current_quiz_questions):
        evaluation_prompt += (
            f"Question {i+1}: {q}\n"
            f"Student Answer: {answers[i]}\n\n"
        )

    evaluation = agent.call_llm([
        {"role": "system", "content": "You are a strict but helpful German examiner."},
        {"role": "user", "content": evaluation_prompt}
    ])

    # Background learning update
    agent.assess_level_and_plan(
        user_input="Quiz completed and evaluated.",
        mode="chat"
    )

    return evaluation

# ---------- UI ----------
with gr.Blocks() as demo:
    gr.Markdown("# 🇩🇪 German C1 Tutor (Agentic AI)")

    # --- Chat ---
    with gr.Tab("Chat"):
        chat_input = gr.Textbox(lines=4, label="Write in German")
        chat_output = gr.Textbox(lines=12, label="Tutor Response")
        gr.Button("Send").click(chat_fn, chat_input, chat_output)

    # --- Lesson ---
    with gr.Tab("Daily Lesson"):
        lesson_output = gr.Textbox(lines=16)
        gr.Button("Generate Lesson").click(lesson_fn, outputs=lesson_output)

    # --- Quiz ---
    with gr.Tab("Daily Quiz"):
        gen_btn = gr.Button("Generate Quiz")

        q1 = gr.Markdown()
        q2 = gr.Markdown()
        q3 = gr.Markdown()
        q4 = gr.Markdown()
        q5 = gr.Markdown()

        a1 = gr.Textbox(lines=3, label="Answer 1")
        a2 = gr.Textbox(lines=3, label="Answer 2")
        a3 = gr.Textbox(lines=3, label="Answer 3")
        a4 = gr.Textbox(lines=4, label="Answer 4 (Paragraph)")
        a5 = gr.Textbox(lines=3, label="Answer 5")

        gen_btn.click(
            populate_quiz_ui,
            outputs=[q1, q2, q3, q4, q5]
        )

        eval_out = gr.Textbox(lines=18, label="Evaluation & Score")
        gr.Button("Submit Answers").click(
            evaluate_quiz,
            inputs=[a1, a2, a3, a4, a5],
            outputs=eval_out
        )

demo.launch(server_name="0.0.0.0", server_port=7860)
