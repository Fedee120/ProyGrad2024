from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import OpenAI, ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from tools.knowledge_base import KnowledgeBase
from prompt.prompt_v2 import PROMPT
from langgraph.prebuilt import create_react_agent


# Initialize the GPT-4o-mini model
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Use your existing KnowledgeBase tool
tools = [KnowledgeBase()]

system_prompt = PROMPT

agent_executor = create_react_agent(model, tools, state_modifier=system_prompt)

# Initialize the prompt template with placeholders for conversation history
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", PROMPT),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

response = agent_executor.invoke({"messages": [("user", "Hola, quiero que me digas cuales son las implicaciones eticas de usar IA generativa en el aula. Soy un docente de secundaria sin mucha experiencia en IA, por lo que quiero una explicacion simple pero completa.")]})
print(response["messages"])
