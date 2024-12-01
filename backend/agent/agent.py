from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from agent.tools.knowledge_base import KnowledgeBase
from dotenv import load_dotenv
from agent.prompt.prompt_v3 import PROMPT
from langsmith import traceable
import os

os.environ['LANGCHAIN_TRACING_V2'] = 'false'
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
os.environ['LANGCHAIN_API_KEY'] = str(os.getenv('LANGCHAIN_API_KEY'))
os.environ['LANGCHAIN_PROJECT'] = 'ProyGrad'

load_dotenv()

class Agent:
    def __init__(self) -> None:
        self.model = ChatOpenAI(model="gpt-4o")
        self.tools = [KnowledgeBase()]
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", PROMPT),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        self.agent = self.create_agent()
        self.agent_executor = self.create_agent_executor(self.agent)

    def create_agent(self):
        return create_tool_calling_agent(self.model, self.tools, self.prompt)
    
    def create_agent_executor(self, agent):
        return AgentExecutor(agent=agent, tools=self.tools)
    
    @traceable
    def invoke(self, message):
        result = self.agent_executor.invoke(message)
        if "output" not in result or not result["output"]:
            raise ValueError("No response from agent")
        return result

if __name__ == "__main__":
    agent = Agent()
    message = "Hola, quiero que me digas cuales son las implicaciones éticas de usar IA generativa en el aula. Soy un docente de secundaria sin mucha experiencia en IA, por lo que quiero una explicación simple pero completa."
    print(agent.invoke({"input": message}))
