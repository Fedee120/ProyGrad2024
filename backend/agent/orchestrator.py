from typing import List, Tuple
from langchain_core.messages import BaseMessage
from agent.knowledge_base import KnowledgeBase
from dotenv import load_dotenv
from agent.prompt.prompt_v4 import PROMPT
from llms.query_filter import QueryFilter
from llms.response_generator import ResponseGenerator
from langsmith import traceable

class ChatOrchestrator:
    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.filter_llm = QueryFilter()
        self.response_llm = ResponseGenerator(PROMPT)

    @traceable
    def process_query(self, query: str, history: List[BaseMessage]) -> Tuple[str, list[str], bool]:
        context = ""
        citations = []

        filter_response = self.filter_llm.filter(query)

        if filter_response.tool_calls:
            search_result = self.knowledge_base.search(query, history)
            
            context = search_result.answer
            citations = [
                context_item.source 
                for context_item in search_result.context
            ]

            if not citations and "No information found" not in context:
                raise ValueError("Citations list is empty but answer is not 'No information found'")
        else:
            context = filter_response.content

        final_response = self.response_llm.generate_response(
            query=query,
            context=context,
            history=history
        )
        
        return final_response, citations, filter_response.tool_calls
    
if __name__ == "__main__":
    load_dotenv()

    orchestrator = ChatOrchestrator()
    print(orchestrator.process_query("Hola, quiero que me digas cuales son las implicaciones éticas de usar IA generativa en el aula. Soy un docente de secundaria sin mucha experiencia en IA, por lo que quiero una explicación simple pero completa."))
