from typing import List, Tuple
from langchain_core.messages import BaseMessage
from agent.knowledge_base import KnowledgeBase
from dotenv import load_dotenv
from llms.pedagogical_response_generator import PedagogicalResponseGenerator
from llms.conversational_response_generator import ConversationalResponseGenerator
from langsmith import traceable
import random

class ChatOrchestrator:
    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.conversational_response_llm = ConversationalResponseGenerator()
        self.pedagogical_response_llm = PedagogicalResponseGenerator()

    @traceable
    def process_query(self, query: str, history: List[BaseMessage]) -> Tuple[str, list[str], bool]:
        context = ""
        citations = []

        # Randomly choose between conversational and pedagogical response with 0.5 probability
        if random.random() < 0.5:
            search_result = self.knowledge_base.search(query, history)
                
            context = search_result.answer
            citations = [
                context_item.source 
                for context_item in search_result.context
            ]

            if not citations and "No information found" not in context:
                raise ValueError("Citations list is empty but answer is not 'No information found'")

            final_response = self.conversational_response_llm.generate_response(
                query=query,
                context=context,
                history=history
            )
        else:
            final_response = self.pedagogical_response_llm.generate_response(
                query=query,
                history=history
            )

        return final_response, citations
    
if __name__ == "__main__":
    load_dotenv()

    orchestrator = ChatOrchestrator()
    print(orchestrator.process_query("Hola, quiero que me digas cuales son las implicaciones éticas de usar IA generativa en el aula. Soy un docente de secundaria sin mucha experiencia en IA, por lo que quiero una explicación simple pero completa.", []))