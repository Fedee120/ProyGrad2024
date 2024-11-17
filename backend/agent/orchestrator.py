from typing import List, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from agent.knowledge_base import KnowledgeBase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from dotenv import load_dotenv
from agent.prompt.prompt_v3 import PROMPT

class ChatOrchestrator:
    def __init__(self):
        load_dotenv()
        
        self.knowledge_base = KnowledgeBase()

        self.filter_llm = ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0
        ).bind_tools([self._search_knowledge])

        self.response_llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7
        )

        self.filter_prompt = """You are a domain expert filter that determines whether queries require searching for information or can be handled directly. 
        Your decision will be used by the response model to determine how to answer the query.
        
        Your role is to:
        1. Call the provided tool when its needed
        2. Specify if no tool call is needed and why
        
        When a tool call is needed:
        - The query is about information
        - The query is about the meaning of something

        When a tool call is not needed:
        - Greetings or casual conversation
        
        Remember you should just filter. You should either call the tool or explain why no tool call is needed. Never provide information by yourself and always call the tool if information is required to be able to cite the sources later on.
        
        Examples:
        - "What is Articial Intelligence?" -> Tool call required
        - "Hello" -> No search done because it's a greeting
        - "What is the capital of France?" -> Tool call required
        - "What is the weather in Tokyo?" -> Tool call required
        - "My name is Juan" -> No search done because it's a casual conversation
        - "What does it mean to clap my hands?" -> Tool call required
        """
        
        self.response_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert assistant that provides information only if it was obtained from the context filter. 
            You should not provide any information that has not been obtained from the context filter.
            Do not add or infer information beyond what's in the context filter.
            If information is provided by the context filter, incorporate it naturally into your response."""),
            ("human", "{query}"),
            ("system", "Context from filter: {context}"),
            ("human", "Generate a helpful response based on the above context. Remember: Your role is to be accurate and helpful while strictly adhering to the information provided by the context filter.")
        ])

    @tool
    def _search_knowledge():
        """Search for specific information in the knowledge base."""
        return 
    
    def process_query(self, query: str) -> Tuple[str, list[str], bool]:
        print("\n" + "="*50 + "\n")
        print(f"Processing query: {query}")
        print("\n" + "="*50 + "\n")
        
        filter_response = self.filter_llm.invoke([
            SystemMessage(content=self.filter_prompt), 
            HumanMessage(content=query)
        ])
        print(f"Filter response: {filter_response}")
        print("\n" + "="*50 + "\n")
        
        context = ""
        citations = []
        
        if filter_response.tool_calls:
            print("Tool call detected - searching knowledge base")
            print("\n" + "="*50 + "\n")
            
            search_result = self.knowledge_base.search(query)
            
            context = search_result.answer
            citations = [
                context_item.source 
                for context_item in search_result.context
            ]
        else:
            print("No tool call detected - using filter response directly")
            print("\n" + "="*50 + "\n")
            context = filter_response.content
            
        print(f"Context: {context}")
        print("\n" + "="*50 + "\n")

        print(f"Citations: {citations}")
        print("\n" + "="*50 + "\n")
        
        final_response = self.response_llm.invoke(
            self.response_prompt.format(
                query=query,
                context=context
            )
        )
        print(f"Final response: {final_response.content}")
        
        return final_response.content, citations, filter_response.tool_calls
    
if __name__ == "__main__":
    orchestrator = ChatOrchestrator()
    print(orchestrator.process_query("Hola, quiero que me digas cuales son las implicaciones éticas de usar IA generativa en el aula. Soy un docente de secundaria sin mucha experiencia en IA, por lo que quiero una explicación simple pero completa."))
