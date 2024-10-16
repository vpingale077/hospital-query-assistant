import gradio as gr
import os
from dotenv import load_dotenv
from hospital_query_app import handle_hospital_query, set_groq_api_key
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize token counter
total_tokens_used = 0
tokens_used = 0

def process_query(message, history, api_key):
    global total_tokens_used, tokens_used
    
    if not api_key:
        return history + [("System", "Please enter your GROQ API key in the input field below.")]
    
    set_groq_api_key(api_key)
    result = handle_hospital_query(message)
    response = result['response']
    tokens_used = result['tokens_used']
    
    total_tokens_used += tokens_used
    
    history.append((message, response))
    return history

def update_token_info():
    return f"Tokens used in last query: {tokens_used}", f"Total tokens used: {total_tokens_used}"

# Custom CSS for smaller font and larger chatbot
custom_css = """
.chatbot-container {
    font-size: 0.5em;
}
"""

with gr.Blocks(theme=gr.themes.Soft(), css=custom_css) as demo:
    gr.Markdown("# Hospital Query Assistant")
    gr.Markdown("Ask questions about hospital services, appointments, and general medical information.")
    
    with gr.Row():
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(height=500, elem_classes="chatbot-container")
            msg = gr.Textbox(placeholder="Type your message here...", label="User Input")
            clear = gr.Button("Clear")
        
        with gr.Column(scale=1):
            token_last = gr.Markdown("Tokens used in last query: 0")
            token_total = gr.Markdown("Total tokens used: 0")
            api_key = gr.Textbox(placeholder="Enter your GROQ API key here", label="GROQ API Key", type="password")
    
    msg.submit(process_query, [msg, chatbot, api_key], chatbot)
    msg.submit(update_token_info, None, [token_last, token_total])
    msg.submit(lambda: "", None, msg)
    clear.click(lambda: None, None, chatbot)
    clear.click(lambda: ("Tokens used in last query: 0", "Total tokens used: 0"), None, [token_last, token_total])
    clear.click(lambda: 0, None, msg)

if __name__ == "__main__":
    demo.launch()
