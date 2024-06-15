import streamlit as st
from trade_agent import GPTAssistant
from streamlit_chat import message

# Initialize the assistant
assistant = GPTAssistant()

# Initialize session state for maintaining the message history if it doesn't already exist
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Streamlit interface setup
st.title('📈FinBot')

# Continuous chat input that automatically manages its state
user_input = st.chat_input("Type your query here...")

if user_input:
    # Append user message to the chat history immediately
    st.session_state.messages.append({'text': user_input, 'is_user': True})

    # Generate a response from the assistant
    response = assistant.conversation(user_input)
    
    # Append assistant's response to the chat history immediately
    st.session_state.messages.append({'text': response, 'is_user': False})

# Display messages using streamlit-chat
# Moved below the input processing to ensure messages are appended before rendering
for message_info in st.session_state.messages:
    message(message_info['text'], is_user=message_info['is_user'])
