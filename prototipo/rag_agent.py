import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from dotenv import load_dotenv
from langsmith import traceable
from prompt import PROMPT

load_dotenv()
API_KEY = os.getenv('OPENAI_API_KEY')
EMBEDDINGS_MODEL = os.getenv('EMBEDDINGS_MODEL')
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
os.environ['LANGCHAIN_API_KEY'] = str(os.getenv('LANGCHAIN_API_KEY'))
os.environ['LANGCHAIN_PROJECT'] = 'ProyGrad'

class RagAgent:
    def __init__(self, session_id, chat_history, llm_model='gpt-3.5-turbo-0125'):
        self.session_id = session_id
        self.chat_history = chat_history
        self.knowledge_base = self.prepare_knowledge_base()
        self.tools = self.create_tools()
        self.prompt = self.set_prompt()
        self.llm = self.set_llm(llm_model)
        self.agent = self.set_executor()
        self.agent_with_history = self.set_chat_with_history()

    def prepare_knowledge_base(self):
        try:
            embeddings = OpenAIEmbeddings(model=EMBEDDINGS_MODEL, api_key=API_KEY)
            db = FAISS.load_local('data_embeddings.db', embeddings=embeddings, allow_dangerous_deserialization=True)
            return db.as_retriever()
        except Exception as e:
            print(e)
            return None
    
    def create_tools(self):
        tool = create_retriever_tool(
            self.knowledge_base,
            'search_artificial_intelligence',
            'Searches and returns excerpts from a knowledge base containing documents about artificial intelligence.',
        )
        tools = [tool]
        return tools
    
    def set_prompt(self):
        prompt = hub.pull('hwchase17/openai-tools-agent')
        prompt[0].prompt.template = PROMPT
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
            runnable=self.agent,
            get_session_history=lambda session_id : self.chat_history,
            history_messages_key='chat_history',
            verbose=True
        )    
        return agent_with_history
    
    @traceable
    def interact_with_agent(self, query):
        response = self.agent_with_history.invoke(
            {'input': query},
            config={'configurable': {'session_id': self.session_id}}
        )
        return response['output']

    def has_credentials(self):
        return API_KEY is not None