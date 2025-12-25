import gradio as gr
from agent_state import AgentState

agent = AgentState()

def chat(msg):
    return agent.assess_level_and_plan(msg)

gr.Interface(
    fn=chat,
    inputs="text",
    outputs="text",
    title="Agentic C1 German Tutor"
).launch(server_name="0.0.0.0", server_port=7860)
