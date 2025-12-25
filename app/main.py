import gradio as gr
from agent_state import AgentState

# Initialize memory backend
agent = AgentState()

# Function to handle user input
def chat_with_agent(user_input):
    # Store user input in FAISS memory
    agent.add_to_faiss(user_input)
    
    # Generate next vocab/grammar prompt (example)
    reply = f"Your input: {user_input}\nNext focus: Learn Konjunktiv II"
    return reply

# Gradio interface
iface = gr.Interface(
    fn=chat_with_agent,
    inputs="text",
    outputs="text",
    title="C1 German Tutor AI",
    description="Chat with your agent to learn German. Daily quizzes included."
)

# Launch interface
if __name__ == "__main__":
    iface.launch(share=True)
