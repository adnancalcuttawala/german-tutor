import gradio as gr
from agent_state import AgentState

agent = AgentState()

def chat(user_message):
    if not user_message.strip():
        return "Please write something in German or English 🙂"
    return agent.assess_level_and_plan(user_message)

demo = gr.Interface(
    fn=chat,
    inputs=gr.Textbox(
        lines=3,
        placeholder="Write something in German (or English to start)..."
    ),
    outputs="text",
    title="🇩🇪 Agentic C1 German Tutor",
    description=(
        "This AI assesses your German level daily, "
        "creates a tailored C1 study plan, "
        "and adapts based on your progress.\n\n"
        "Runs fully on free-tier infrastructure."
    ),
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
