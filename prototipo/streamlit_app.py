import streamlit as st
import uuid
from langchain_community.chat_message_histories import ChatMessageHistory
from rag_agent import RagAgent

st.title('Asistente Virtual para Docentes: Integrando IA en la Educación')

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = ChatMessageHistory()

if 'messages' not in st.session_state:
    st.session_state.messages = []

agent = RagAgent(session_id=st.session_state['session_id'], chat_history=st.session_state['chat_history'], llm_model='gpt-3.5-turbo-0125') # llm_model='gpt-4o' para evaluar el contenido de la respuesta

with st.sidebar:
    st.title('Comunicación con OpenAI')

    if agent.has_credentials():
        st.success('Credenciales configuradas!', icon='✅')
    else:
        st.error('Credenciales no configuradas. Por favor revise su configuración.', icon='❌')

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if query := st.chat_input('Haz un pregunta...'):
    st.chat_message('user').markdown(query)
    st.session_state.messages.append({'role': 'user', 'content': query})
    response = agent.interact_with_agent(query)
    st.chat_message('assistant').markdown(response)
    st.session_state.messages.append({'role': 'assistant', 'content': response})
