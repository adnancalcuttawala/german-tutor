import gradio as gr
from agent_state import AgentState

agent = AgentState()

# ---------------- Chat ----------------
def chat_fn(msg):
    return agent.assess_level_and_plan(user_input=msg, mode="chat")

# ---------------- Lesson ----------------
def lesson_fn():
    return agent.assess_level_and_plan(mode="lesson")

# ---------------- Quiz ----------------
def generate_quiz():
    """
    Generate daily quiz as a list of questions
    """
    quiz_text = agent.assess_level_and_plan(mode="quiz")
    
    # Simple split by newline; could be improved to parse numbered questions
    questions = [q.strip() for q in quiz_text.split("\n") if q.strip()]
    
    # Store questions in agent state for evaluation later
    agent.current_quiz_questions = questions
    return questions

def evaluate_quiz(*answers):
    """
    Evaluate user's answers with LLM and return score + feedback
    """
    if not hasattr(agent, "current_quiz_questions"):
        return "No quiz generated yet."
    
    evaluation_prompt = "You are a German C1 teacher. Evaluate the following student answers, give feedback, and score out of 10.\n\n"
    for i, q in enumerate(agent.current_quiz_questions):
        student_answer = answers[i] if i < len(answers) else ""
        evaluation_prompt += f"Q{i+1}: {q}\nStudent Answer: {student_answer}\n\n"
    
    # LLM evaluates answers
    evaluation = agent.call_llm(evaluation_prompt)
    
    # Also update daily plan / assessment internally
    agent.assess_level_and_plan(user_input="Evaluation complete for quiz", mode="chat")
    
    return evaluation

# ---------------- Gradio Interface ----------------
with gr.Blocks() as demo:
    gr.Markdown("# German C1 Tutor 🤖🇩🇪")

    # --- Chat Tab ---
    with gr.Tab("Chat"):
        chat_input = gr.Textbox(label="Your message", lines=3, placeholder="Schreibe hier...", interactive=True)
        chat_output = gr.Textbox(label="Tutor response", lines=10)
        chat_button = gr.Button("Send")
        chat_button.click(chat_fn, inputs=chat_input, outputs=chat_output)

    # --- Daily Lesson Tab ---
    with gr.Tab("Daily Lesson"):
        lesson_button = gr.Button("Generate Lesson")
        lesson_output = gr.Textbox(label="Today's Lesson", lines=15)
        lesson_button.click(lesson_fn, inputs=[], outputs=lesson_output)

    # --- Daily Quiz Tab ---
    with gr.Tab("Daily Quiz"):
        quiz_button = gr.Button("Generate Quiz")
        quiz_output = gr.Column()  # will hold dynamic questions
        submit_button = gr.Button("Submit Answers")
        evaluation_output = gr.Textbox(label="Evaluation & Feedback", lines=15)
        
        # Function to dynamically create input boxes for each question
        def create_quiz_inputs():
            questions = generate_quiz()
            inputs = []
            for q in questions:
                gr.Markdown(f"**Question:** {q}")
                tb = gr.Textbox(label="Your Answer", lines=2)
                inputs.append(tb)
            return inputs
        
        quiz_inputs = create_quiz_inputs()
        submit_button.click(fn=evaluate_quiz, inputs=quiz_inputs, outputs=evaluation_output)

demo.launch(share=True, server_name="0.0.0.0", server_port=7860)
