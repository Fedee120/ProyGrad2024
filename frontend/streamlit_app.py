import streamlit as st
import uuid
import requests
import logging

BACKEND_URL = 'http://backend:8080'

# Configure logging
logging.basicConfig(level=logging.INFO)

def check_backend_status():
    try:
        response = requests.get(f"{BACKEND_URL}/check_status")
        response.raise_for_status()
        data = response.json()
        if data.get('status') == 'success':
            return True, 'Backend is up!'
        else:
            return False, 'Backend is down.'
    except requests.RequestException as e:
        logging.error(f'Error checking backend status: {e}')
        return False, f'Error checking backend status: {e}'

def send_query_to_backend(query):
    try:
        response = requests.post(f"{BACKEND_URL}/invoke_agent", json={'message': query})
        response.raise_for_status()
        data = response.json()
        return data.get('data', 'No response from backend.')
    except requests.RequestException as e:
        logging.error(f'Error communicating with backend: {e}')
        return f'Error communicating with backend: {e}'

# Initialize session state variables
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display sidebar
with st.sidebar:
    st.title('Comunicación con OpenAI')
    backend_status, backend_message = check_backend_status()
    if backend_status:
        st.success(backend_message, icon='✅')
    else:
        st.error(backend_message, icon='❌')

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if query := st.chat_input('Haz un pregunta...'):
    st.chat_message('user').markdown(query)
    st.session_state.messages.append({'role': 'user', 'content': query})

    assistant_response = send_query_to_backend(query)
    st.chat_message('assistant').markdown(assistant_response)
    st.session_state.messages.append({'role': 'assistant', 'content': assistant_response})
