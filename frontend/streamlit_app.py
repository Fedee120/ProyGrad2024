import streamlit as st
import uuid
import requests

# Initialize session state variables
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())

if 'messages' not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title('Comunicación con OpenAI')

    # Assuming your backend has an endpoint to check credentials
    # response = requests.get(f"{backend_url}/check_credentials")
    # if response.status_code == 200 and response.json().get('status') == 'success':
    #     st.success('Credenciales configuradas!', icon='✅')
    # else:
    #     st.error('Credenciales no configuradas. Por favor revise su configuración.', icon='❌')

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if query := st.chat_input('Haz un pregunta...'):
    st.chat_message('user').markdown(query)
    st.session_state.messages.append({'role': 'user', 'content': query})

    # Send the query to the backend API
    response = requests.post("http://localhost:8080/invoke_agent", json={'message': query})
    
    if response.status_code == 200:
        response_data = response.json()
        assistant_response = response_data.get('response', 'No response from backend.')
    else:
        assistant_response = 'Error communicating with backend.'

    st.chat_message('assistant').markdown(assistant_response)
    st.session_state.messages.append({'role': 'assistant', 'content': assistant_response})