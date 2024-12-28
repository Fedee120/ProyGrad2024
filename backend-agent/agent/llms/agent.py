import os
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent
from langchain.tools import tool
from agent.knowledge_base import KnowledgeBase
from agent.prompt.prompt_v4 import PROMPT

from dotenv import load_dotenv

load_dotenv()
 
API_KEY  = os.getenv('OPENAI_API_KEY')

knowledge_base = KnowledgeBase()

class RagAgent:
    def __init__(self, session_id, llm_model="gpt-4o"):
        self.session_id = session_id
        self.tools = self.create_tools()
        self.prompt = self.set_prompt()
        self.llm = self.set_llm(llm_model)
        self.agent = self.set_executor()

    @tool(response_format="content_and_artifact")
    def search(query: str):
        """
        Realiza una búsqueda en la base de conocimientos utilizando el sistema RAG.

        Args:
            query (str): La consulta o pregunta del usuario.

        Returns:
            tuple: Una tupla que contiene la respuesta generada y los documentos relevantes encontrados.
        """
        response = knowledge_base.search(query)
        return response
    
    def create_tools(self):
        tools = [self.search]
        return tools
    
    def set_prompt(self):
        prompt = hub.pull("hwchase17/react-chat")
        return prompt
    
    def set_llm(self, model):
        llm = ChatOpenAI(temperature=0.5, model=model, api_key=API_KEY)
        return llm

    def set_executor(self):
        agent = create_react_agent(self.llm, self.tools, self.prompt)
        return agent

    def interact_with_agent(self, prompt):
        response = self.agent.invoke({"input": prompt}, config={"configurable": {"session_id": self.session_id}})
        return response


if __name__ == "__main__":
    rag = RagAgent(session_id=0, llm_model="gpt-4o")
    response = rag.interact_with_agent("¿Cuál es el objetivo principal de la IA en la educación según el documento?")
    print(response)