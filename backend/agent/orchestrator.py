from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from tools.knowledge_base import KnowledgeBase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool


class ChatOrchestrator:
    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.filter_llm = ChatOpenAI(
            model="gpt-4o", 
            temperature=0
        ).bind_tools([self.search_knowledge])
        
        self.response_llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7
        )

        self.filter_prompt = """You are a domain expert filter that determines whether queries require searching for information or can be handled directly.

        Your role is to:
        1. Call the provided tool when its needed
        2. Specify if no tool call is needed and why
        
        When a tool call is needed:
        - The query is about information

        When a tool call is not needed:
        - Greetings or casual conversation
        
        Remember you should just filter. You should either call the tool or explain why no tool is needed.
        
        Examples:
        - "What is Articial Intelligence?" -> tool call
        - "Hello" -> no tool call (greeting)
        - "What is the capital of France?" -> tool call
        - "What is the weather in Tokyo?" -> tool call
        - "Me llamo Juan" -> no tool call (casual conversation)
        """
        
        self.response_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert assistant that provides information only if it was obtained from the context filter. 
            You should not provide any information that has not been obtained from the context filter.
            If search results are provided and contain relevant information, incorporate that technical information naturally."""),
            ("human", "{query}"),
            ("system", "Context from filter: {context}"),
            ("human", "Generate a helpful response based on the above context.")
        ])

    @tool
    def search_knowledge():
        """Search for specific information in the knowledge base."""
        return 

    def process_query(self, query: str) -> str:
        # Get filter LLM's response with potential tool usage
        print(f"Processing query: {query}")
        filter_response = self.filter_llm.invoke([
            SystemMessage(content=self.filter_prompt), 
            HumanMessage(content=query)
        ])
        print(f"Filter LLM response: {filter_response}")
        
        # Check if there are any tool calls
        context = None
        if filter_response.tool_calls:
            print(filter_response.tool_calls)
            print("Tool call detected - searching knowledge base")
            # Execute the tool call
            search_result = self.knowledge_base.run({"query": query, "fallback": "No information found"})
            context = f"Retrieved information: {search_result}"
            print(f"Search result: {search_result}")
        else:
            # Use the direct response from filter LLM if no tool was called
            print("No tool call - using direct filter response")
            context = filter_response.content
            
        # Generate final response using response LLM
        print("Generating final response")
        final_response = self.response_llm.invoke(
            self.response_prompt.format(
                query=query,
                context=context
            )
        )
        print(f"Final response generated: {final_response.content}")
        
        return final_response.content