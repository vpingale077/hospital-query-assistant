# Hospital Query Assistant

This project implements a Hospital Query Assistant using AutoGen and GroqCloud API, with a Gradio-based user interface. The assistant helps users with queries about hospital services, appointments, and general medical information.

## Features

- Natural language processing for hospital-related queries
- Content moderation to ensure safe and appropriate responses
- Token usage tracking
- User-friendly chat interface

## Implementation Details

### Backend (`hospital_query_app.py`)

The backend is implemented using AutoGen and the GroqCloud API. Key components include:

1. **AutoGen Agents**:
   - User Proxy Agent: Represents the user in the conversation.
   - Hospital Assistant Agent: Provides responses to user queries.

2. **Content Moderation**:
   - Uses the Mixtral-8x7b-32768 model to check for inappropriate content.
   - Ensures queries are safe and relevant before processing.

3. **Query Handling**:
   - Sanitizes user input to remove potential security risks.
   - Processes queries using the Hospital Assistant Agent.
   - Tracks token usage for each query.

### Frontend (`hospital_query_ui.py`)

The frontend is built using Gradio, providing a web-based user interface. Features include:

1. **Chat Interface**:
   - Displays conversation history.
   - Allows users to input queries easily.

2. **Token Usage Display**:
   - Shows tokens used in the last query.
   - Displays total tokens used in the session.

3. **Clear Functionality**:
   - Allows users to reset the conversation and token counters.

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/vpingale077/hospital-query-assistant.git
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the project root.
   - Add your GroqCloud API key:
     ```
     GROQ_API_KEY=your_api_key_here
     ```

4. Run the application:
   ```
   python hospital_query_ui.py
   ```

## Usage

1. Launch the application using the command above.
2. Open the provided URL in your web browser.
3. Type your hospital-related query in the input box and press Enter.
4. View the assistant's response in the chat interface.
5. Check token usage information on the right side of the interface.

## Note

This assistant is designed for general information purposes only and should not be used for personal medical advice or diagnoses.

## License

[MIT License](LICENSE)
