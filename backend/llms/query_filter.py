from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain_core.tools import tool

class QueryFilter:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0
        ).bind_tools([self._search_knowledge])

        self.prompt = """You are a domain expert filter that determines whether queries require searching for information or can be handled directly. 
        Your decision will be used by the response model to determine how to answer the query.
        
        Your role is to:
        1. Call the provided tool when its needed
        2. Specify if no tool call is needed and why
        
        When a tool call is needed:
        - The query is about information
        - The query is about the meaning of something
        - The query is about how to do something
        - The query is about a concern or reflection
        - The query is about a debate or discussion
        - The query is about past messages in the conversation no matter the lack of context (e.g. "Can you explain that last part again?" or "Tell me more about what you just said")

        When a tool call is not needed:
        - Greetings or casual conversation
        
        Remember you should just filter. You should either call the tool or explain why no tool call is needed. Never provide information by yourself and always call the tool if the topic has factual information that could enrich the conversation.
        
        Examples:
        - "What is Articial Intelligence?" -> Tool call required
        - "Hello" -> No search done because it's a greeting
        - "What is the capital of France?" -> Tool call required
        - "What is the weather in Tokyo?" -> Tool call required
        - "My name is Juan" -> No search done because it's a casual conversation
        - "What does it mean to clap my hands?" -> Tool call required
        """

    @tool
    def _search_knowledge(self):
        """Search for specific information in the knowledge base."""
        return

    def filter(self, query: str) -> BaseMessage:
        """Filter a query to determine if knowledge base search is needed."""
        return self.llm.invoke([
            SystemMessage(content=self.prompt),
            HumanMessage(content=query)
        ]) 