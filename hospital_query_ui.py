import gradio as gr
import os
from dotenv import load_dotenv
from hospital_query_app import handle_hospital_query
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize token counter
total_tokens_used = 0
tokens_used = 0

def process_query(message, history):
    global total_tokens_used, tokens_used
    
    result = handle_hospital_query(message)
    response = result['response']
    tokens_used = result['tokens_used']
    
    total_tokens_used += tokens_used
    
    history.append((message, response))
    return history

def update_token_info():
    return f"Tokens used in last query: {tokens_used}", f"Total tokens used: {total_tokens_used}"

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Hospital Query Assistant")
    gr.Markdown("Ask questions about hospital services, appointments, and general medical information.")
    
    with gr.Row():
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(height=400)
            msg = gr.Textbox(placeholder="Type your message here...", label="User Input")
            clear = gr.Button("Clear")
        
        with gr.Column(scale=1):
            token_last = gr.Markdown("Tokens used in last query: 0")
            token_total = gr.Markdown("Total tokens used: 0")
    
    msg.submit(process_query, [msg, chatbot], chatbot)
    msg.submit(update_token_info, None, [token_last, token_total])
    msg.submit(lambda: "", None, msg)
    clear.click(lambda: None, None, chatbot)
    clear.click(lambda: ("Tokens used in last query: 0", "Total tokens used: 0"), None, [token_last, token_total])
    clear.click(lambda: 0, None, msg)

if __name__ == "__main__":
    demo.launch()
