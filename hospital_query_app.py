import os
import autogen
from groq import Groq
from dotenv import load_dotenv
from typing import Dict, Any
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Initialize GroqCloud client and agents
groq_client = None
GROQ_API_KEY = None
user_proxy = None
hospital_assistant = None

def set_groq_api_key(api_key: str):
    global groq_client, GROQ_API_KEY, user_proxy, hospital_assistant
    GROQ_API_KEY = api_key
    groq_client = Groq(api_key=GROQ_API_KEY)
    os.environ["OPENAI_API_KEY"] = GROQ_API_KEY  # Set the environment variable for OpenAI compatibility

    # Configuration for AutoGen agents
    config_list = [
        {
            "model": "mixtral-8x7b-32768",
            "api_key": GROQ_API_KEY,
        }
    ]

    llm_config = {
        "config_list": config_list,
        "cache_seed": 42,
        "temperature": 0.5,
        "base_url": "https://api.groq.com/openai/v1",
    }

    # Disable Docker for code execution
    code_execution_config = {"use_docker": False}

    # Create User Proxy Agent
    user_proxy = autogen.UserProxyAgent(
        name="User_Proxy",
        system_message="A human user interacting with the hospital query system.",
        human_input_mode="NEVER",
        code_execution_config=code_execution_config,
    )

    # Create Hospital Query Assistant
    hospital_assistant = autogen.AssistantAgent(
        name="Hospital_Assistant",
        system_message="You are a hospital assistant AI. You help users with their queries about hospital services, appointments, and general medical information. Provide concise and helpful responses. Do not provide any personal medical advice or diagnoses.",
        llm_config=llm_config,
    )

    logging.info("AutoGen agents created successfully with the provided API key.")

# Define LLAMA_GUARD_PROMPT
LLAMA_GUARD_PROMPT = """
You are an AI content moderation system. Your task is to analyze the given text and determine if it contains any inappropriate content, such as profanity, hate speech, or sensitive medical information. Respond with either "SAFE" or "UNSAFE", followed by a brief explanation.

Text to moderate: {text}

Response:
"""

def sanitize_input(text: str) -> str:
    # Remove any potential HTML or script tags
    text = re.sub(r'<[^>]*?>', '', text)
    # Remove any non-alphanumeric characters except common punctuation
    text = re.sub(r'[^a-zA-Z0-9\s.,!?-]', '', text)
    return text.strip()

def moderate_content(text: str) -> Dict[str, Any]:
    try:
        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",  # Using Mixtral as Llama Guard is not available on Groq
            messages=[
                {"role": "system", "content": "You are a content moderation system."},
                {"role": "user", "content": LLAMA_GUARD_PROMPT.format(text=text)},
            ],
            max_tokens=100,
        )
        moderation_result = response.choices[0].message.content.strip()
        is_safe = moderation_result.lower().startswith("safe")
        logging.info(f"Moderation result: {moderation_result}")
        return {
            "is_safe": is_safe, 
            "explanation": moderation_result,
            "tokens_used": response.usage.total_tokens
        }
    except Exception as e:
        logging.error(f"Error in content moderation: {str(e)}")
        return {"is_safe": False, "explanation": "Error in content moderation", "tokens_used": 0}

def handle_hospital_query(user_input: str) -> Dict[str, Any]:
    global groq_client, GROQ_API_KEY, user_proxy, hospital_assistant
    if not groq_client or not GROQ_API_KEY or not user_proxy or not hospital_assistant:
        return {
            "response": "Please enter your GROQ API key in the input field above.",
            "tokens_used": 0
        }
    
    try:
        sanitized_input = sanitize_input(user_input)
        
        moderation_result = moderate_content(sanitized_input)
        if not moderation_result["is_safe"]:
            return {
                "response": f"I apologize, but I cannot process this query. {moderation_result['explanation']}",
                "tokens_used": moderation_result["tokens_used"]
            }

        response = hospital_assistant.generate_reply(
            messages=[{"role": "user", "content": sanitized_input}],
            sender=user_proxy,
        )
        
        # Assuming the response is a string, we need to get token usage from the Groq client
        assistant_response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": sanitized_input}],
            max_tokens=500,
        )
        
        return {
            "response": response,
            "tokens_used": moderation_result["tokens_used"] + assistant_response.usage.total_tokens
        }
    except Exception as e:
        logging.error(f"Error in handling hospital query: {str(e)}")
        return {
            "response": f"I apologize, but I encountered an error while processing your query: {str(e)}. Please try again later.",
            "tokens_used": 0
        }

# Main application loop (if running directly)
if __name__ == "__main__":
    print("Welcome to the Hospital Query System. Type 'exit' to quit.")
    api_key = input("Please enter your GROQ API key: ")
    set_groq_api_key(api_key)
    total_tokens = 0
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() == "exit":
                break
            result = handle_hospital_query(user_input)
            print(f"Assistant: {result['response']}")
            print(f"Tokens used: {result['tokens_used']}")
            total_tokens += result['tokens_used']
            print(f"Total tokens used: {total_tokens}")
        except KeyboardInterrupt:
            print("\nExiting the application...")
            break
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            print("An unexpected error occurred. Please try again.")
