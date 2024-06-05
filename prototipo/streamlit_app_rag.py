import streamlit as st
import uuid
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
API_KEY = os.getenv('OPENAI_API_KEY')

class RagAgent:
    def __init__(self, session_id, llm_model="gpt-3.5-turbo-0125"):
        self.session_id = session_id
        self.knowledge_base = self.prepare_knowledge_base()
        self.tools = self.create_tools()
        self.prompt = self.set_prompt()
        self.llm = self.set_llm(llm_model)
        self.agent = self.set_executor()
        self.agent_with_history = self.set_chat_with_history()

    def prepare_knowledge_base(self):
        try:
            # loader = PyPDFLoader("data_light.pdf")
            # documents = loader.load()
            # text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=0)
            # texts = text_splitter.split_documents(documents)
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=API_KEY)
            # db = FAISS.from_documents(texts, embeddings)
            db = FAISS.load_local("data_embeddings.db", embeddings=embeddings, allow_dangerous_deserialization=True)
            return db.as_retriever()
        except Exception as e:
            print(e)
            return None
    
    def create_tools(self):
        tool = create_retriever_tool(
            self.knowledge_base,
            "retrieve_from_knowledge_base",
            "Searches and returns excerpts from the knowledge base related to the input query",
        )
        tools = [tool]
        return tools
    
    def set_prompt(self):
        prompt = hub.pull("hwchase17/openai-tools-agent")
        prompt[0].prompt.template = '''
        You are a chatbot designed to assist educators at secondary and university levels who are curious about generative artificial 
        intelligence and the creation of educational tools. Equipped with a feature that searches through extensive knowledge bases, 
        you retrieve text snippets relevant to user queries.

        Your conversations aim to be empathetic and engaging, always striving to spark curiosity and foster learning about 
        generative AI and educational tools. Importantly, you employ the pedagogical technique of prompting further questions 
        to encourage users to think deeply. Instead of providing direct answers, you often ask users how they might apply these 
        concepts and tools in their classrooms or activities, fostering reflection and deeper understanding.

        The chatbot should not invent information and always provide references when possible (provide the document from where the excerpt was extracted). 
        If you don't know the answer to a question, it's okay to say so or acknowledge that you 
        don't have the necessary information to respond.

        You are programmed to be fun, informative, pedagogical, energetic, 
        empathetic, and friendly, perfect for users with very little prior knowledge of AI. 
        Additionally, you are capable of conducting interactive activities to enhance the learning experience.
        '''
        return prompt
    
    def set_llm(self, model):
        llm = ChatOpenAI(temperature=0.5, model=model, api_key=API_KEY)
        return llm

    def set_executor(self):
        agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.tools, return_intermediate_steps=True, verbose=True)
        return agent_executor

    def set_chat_with_history(self):
        agent_with_history = RunnableWithMessageHistory(
            self.agent,
            lambda session_id : st.session_state['chat_history'],
            history_messages_key="chat_history",
            verbose=True
        )    
        return agent_with_history
    
    def interact_with_agent(self, prompt):
        print("Current session ID:", self.session_id)
        response = self.agent_with_history.invoke(
            {"input": prompt},
            config={"configurable": {"session_id": self.session_id}}
        )
        return response['output']
    
    def has_kb(self):
        return self.knowledge_base is not None

    def has_credentials(self):
        return API_KEY is not None

st.title('Asistente virtual de tecnologías de la educación')

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())

session_id_field = st.text_input("Ingrese el session ID:", value=st.session_state['session_id'], key='session_id_field', disabled=True)

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = ChatMessageHistory()

agent = RagAgent(st.session_state['session_id'], llm_model="gpt-4o")

with st.sidebar:
    st.title('Comunicación con OpenAI')

    if agent.has_credentials():
        st.success('Credenciales configuradas!', icon='✅')
    else:
        st.error('Credenciales no configuradas. Por favor revise su configuración.', icon='❌')

if "messages" not in st.session_state:
    st.session_state.messages = []

if prompt := st.chat_input("Haz un pregunta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = agent.interact_with_agent(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
