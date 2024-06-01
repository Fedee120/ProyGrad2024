import streamlit as st
import rag_lib as rlib
import uuid

st.title('Asistente virtual de tecnologías de la educación')

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())

session_id = st.text_input("Ingrese el session ID:", value=st.session_state['session_id'], key='session_id', disabled=True)

agent = rlib.RagAgent(session_id, llm_model="gpt-4o")

with st.sidebar:
    st.title('Comunicación con OpenAI')

    if agent.has_credentials():
        st.success('Credenciales configuradas!', icon='✅')
    else:
        st.error('Credenciales no configuradas. Por favor revise su configuración.', icon='❌')

if "messages" not in st.session_state:
    st.session_state.messages = []

if prompt := st.chat_input("Hola, ¿Cómo puedo asistirte hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = agent.interact_with_agent(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
