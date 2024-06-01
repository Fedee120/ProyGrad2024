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
 
API_KEY  = os.getenv('OPENAI_API_KEY')

class RagAgent:
    def __init__(self, session_id, llm_model="gpt-3.5-turbo-0125"):
        self.session_id = session_id
        self.knowledge_base = self.prepare_knowledge_base()
        self.tools = self.create_tools()
        self.prompt = self.set_prompt()
        self.llm = self.set_llm(llm_model)
        self.agent = self.set_executor()
        self.agent_with_history = self.set_chat_with_history(self.agent)

    def prepare_knowledge_base(self):
        try:
            loader = PyPDFLoader("data.pdf")
            documents = loader.load()
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            texts = text_splitter.split_documents(documents)
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            db = FAISS.from_documents(texts, embeddings)
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
        prompt[0].prompt.template = '''Eres un asistente al que los docentes y 
                                    estudiantes de nivel secundario y universitario consultan sobre la inteligencia artifical generativa y 
                                    creacion de herramientas en educacion. Para ayudar al usuario cuentas con una herramienta que busca en tus conocimientos fragmentos de texto 
                                    relacionados con la consulta del usuario, usala cuando necesites recuperar informacion de tus conocimientos.
                                    Debes tener una conversacion empatica con el usuario y responder intentando incentivar la curiosidad y el aprendizaje. 
                                    Recuerda que tu objetivo es ayudar al usuario a aprender sobre la inteligencia artificial generativa y la creacion de herramientas en educacion, 
                                    por lo que es deseable hacer que el usuario reflexione por ejemplo sobre como puede aplicar herramientas en su aula.
                                    No inventes informacion y siempre que puedas proporciona referencias a tus respuestas. Si no sabes la respuesta a una pregunta,
                                    puedes decir que no sabes la respuesta o que no tienes la informacion necesaria para responder la pregunta.
                                    '''
        return prompt
    
    def set_llm(self, model):
        llm = ChatOpenAI(temperature=0.5, model=model, api_key=API_KEY)
        return llm

    def set_executor(self):
        agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.tools, return_intermediate_steps=True, verbose=True)
        return agent_executor

    def interact_with_agent(self, prompt):
        response = self.agent_with_history.invoke({"input": prompt}, config={"configurable": {"session_id": self.session_id}})
        return response['output']

    def has_kb(self):
        return self.knowledge_base is not None

    def has_credentials(self):
        return API_KEY is not None

    def set_chat_with_history(self, history):
        message_history = ChatMessageHistory()
        agent_with_history = RunnableWithMessageHistory(
            self.agent,
            lambda session_id : message_history,
            history_messages_key="chat_history",
            verbose=True
        )    
        return agent_with_history


if __name__ == "__main__":
    rag = RagAgent(session_id=0, llm_model="gpt-4o")
    response = rag.interact_with_agent("¿Cuál es el objetivo principal de la IA en la educación según el documento?")
    print(response['output'])