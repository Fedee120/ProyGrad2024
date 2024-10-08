# app.py

import streamlit as st
import uuid
import requests

st.title('Asistente Virtual para Docentes: Integrando IA en la Educación')

API_URL = 'http://localhost:8000/chat'  # Asegúrate de que este puerto coincide con el backend

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())

if 'messages' not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title('Comunicación con OpenAI')
    # Aquí podrías agregar opciones adicionales o configuraciones

# Mostrar mensajes de chat desde el historial en la aplicación
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if query := st.chat_input('Haz una pregunta...'):
    st.chat_message('user').markdown(query)
    st.session_state.messages.append({'role': 'user', 'content': query})

    # Enviar la consulta al backend
    payload = {
        'session_id': st.session_state['session_id'],
        'query': query
    }
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        assistant_response = data['response']
    except requests.exceptions.RequestException as e:
        assistant_response = "Error al comunicarse con el backend: {}".format(e)

    st.chat_message('assistant').markdown(assistant_response)
    st.session_state.messages.append({'role': 'assistant', 'content': assistant_response})
