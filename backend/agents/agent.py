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
                ("system", "You are a helpful assistant. When answering information questions use the Knowledge_Base tool, you will receive an answer and relevant context. Use this information to provide a comprehensive and accurate response to the user's query. If the Knowledge_Base doesn't provide a satisfactory answer, say that you don't have the necessary information to answer the question."),
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
    
    def invoke(self, message):
        result = self.agent_executor.invoke(message)
        if "output" not in result or not result["output"]:
            raise ValueError("No response from agent")
        return result

if __name__ == "__main__":
    agent = Agent()
    message = "Hola, quiero que me digas cuales son las implicaciones éticas de usar IA generativa en el aula. Soy un docente de secundaria sin mucha experiencia en IA, por lo que quiero una explicación simple pero completa."
    print(agent.invoke({"input": message}))
