import gradio as gr
from agent_state import AgentState

agent = AgentState()

# ============================================================
# CHAT
# ============================================================
def chat_fn(msg):
    return agent.assess_level_and_plan(user_input=msg, mode="chat")


# ============================================================
# DAILY LESSON
# ============================================================
def lesson_fn():
    return agent.assess_level_and_plan(mode="lesson")


# ============================================================
# QUIZ GENERATION (SAFE)
# ============================================================
def generate_quiz():
    """
    Generate daily quiz as a list of questions.
    Handles string / list / other safely.
    """
    quiz_data = agent.assess_level_and_plan(mode="quiz")

    if isinstance(quiz_data, str):
        questions = [q.strip() for q in quiz_data.split("\n") if q.strip()]
    elif isinstance(quiz_data, list):
        questions = [str(q).strip() for q in quiz_data if str(q).strip()]
    else:
        questions = [str(quiz_data)]

    # Limit to 5 questions for UI stability
    questions = questions[:5]

    agent.current_quiz_questions = questions
    return questions


def populate_quiz_ui():
    """
    Called when 'Generate Quiz' is clicked.
    Returns questions + placeholders for answers.
    """
    questions = generate_quiz()

    # Ensure exactly 5 slots for Gradio
    padded_questions = questions + [""] * (5 - len(questions))

    return padded_questions


# ============================================================
# QUIZ EVALUATION
# ============================================================
def evaluate_quiz(a1, a2, a3, a4, a5):
    if not hasattr(agent, "current_quiz_questions"):
        return "❌ No quiz generated yet."

    answers = [a1, a2, a3, a4, a5]

    evaluation_prompt = (
        "You are a strict but helpful German C1 examiner.\n"
        "Evaluate the student's answers.\n"
        "- Give feedback per question\n"
        "- Correct grammar and style\n"
        "- Give a final score out of 10\n\n"
    )

    for i, question in enumerate(agent.current_quiz_questions):
        evaluation_prompt += (
            f"Question {i+1}: {question}\n"
            f"Student Answer: {answers[i]}\n\n"
        )

    evaluation = agent.call_llm(evaluation_prompt)

    # Background assessment update
    agent.assess_level_and_plan(
        user_input="Daily quiz evaluated.",
        mode="assessment"
    )

    return evaluation


# ============================================================
# GRADIO UI
# ============================================================
with gr.Blocks() as demo:
    gr.Markdown("# 🇩🇪 German C1 Tutor 🤖")
    gr.Markdown("Personalized training, daily lessons & adaptive quizzes")

    # ---------------- CHAT TAB ----------------
    with gr.Tab("Chat"):
        chat_input = gr.Textbox(
            label="Your message",
            lines=5,
            placeholder="Schreibe hier auf Deutsch…",
        )
        chat_output = gr.Textbox(
            label="Tutor response",
            lines=12
        )
        gr.Button("Send").click(chat_fn, chat_input, chat_output)

    # ---------------- LESSON TAB ----------------
    with gr.Tab("Daily Lesson"):
        lesson_output = gr.Textbox(
            label="Today's Lesson",
            lines=18
        )
        gr.Button("Generate Lesson").click(lesson_fn, outputs=lesson_output)

    # ---------------- QUIZ TAB ----------------
    with gr.Tab("Daily Quiz"):
        quiz_button = gr.Button("Generate Quiz")

        q1 = gr.Markdown()
        q2 = gr.Markdown()
        q3 = gr.Markdown()
        q4 = gr.Markdown()
        q5 = gr.Markdown()

        a1 = gr.Textbox(label="Answer 1", lines=3)
        a2 = gr.Textbox(label="Answer 2", lines=3)
        a3 = gr.Textbox(label="Answer 3", lines=3)
        a4 = gr.Textbox(label="Answer 4", lines=3)
        a5 = gr.Textbox(label="Answer 5", lines=4)

        quiz_button.click(
            populate_quiz_ui,
            outputs=[q1, q2, q3, q4, q5]
        )

        submit_btn = gr.Button("Submit Answers")
        evaluation_output = gr.Textbox(
            label="Evaluation & Score",
            lines=18
        )

        submit_btn.click(
            evaluate_quiz,
            inputs=[a1, a2, a3, a4, a5],
            outputs=evaluation_output
        )


# ============================================================
# LAUNCH (Render + local compatible)
# ============================================================
demo.launch(
    server_name="0.0.0.0",
    server_port=7860
)
