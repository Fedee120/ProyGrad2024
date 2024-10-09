from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from tools.knowledge_base import KnowledgeBase
from dotenv import load_dotenv

load_dotenv()

class Agent:
    def __init__(self) -> None:
        self.model = ChatOpenAI(model="gpt-4o")
        self.tools = [KnowledgeBase()]
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant"),
                ("human", "{input}"),
                # Placeholders fill up a **list** of messages
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        self.agent = self.create_agent()
        self.agent_executor = self.create_agent_executor(self.agent)
        pass

    def create_agent(self):
        return create_tool_calling_agent(self.model, self.tools, self.prompt)
    
    def create_agent_executor(self, agent):
        return AgentExecutor(agent=agent, tools=self.tools)
    
    def invoke(self, message):
        return self.agent_executor.invoke(message)


agent = Agent()
message = "Hola, quiero que me digas cuales son las implicaciones éticas de usar IA generativa en el aula. Soy un docente de secundaria sin mucha experiencia en IA, por lo que quiero una explicación simple pero completa."
print(agent.agent_executor.invoke({"input": message}))

