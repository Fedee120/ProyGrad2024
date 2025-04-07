from typing import List, Tuple, Literal
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
from .rag import RAG
from .llms.pedagogical_response_generator import PedagogicalResponseGenerator
from .llms.conversational_response_generator import ConversationalResponseGenerator
from .llms.no_retrieval_response_generator import NoRetrievalResponseGenerator
from .llms.deny_response_generator import DenyResponseGenerator
from langsmith import traceable
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os

class RouterResponse(BaseModel):
    """The decision path for handling a user's query."""
    decision_path: Literal["no-retrieval reply", "retrieve", "cross-question", "deny"] = Field(
        description="Given a user question and the conversation history, choose which decision path would be most appropriate for answering their question."
    )
    reasoning_steps: str = Field(..., description="List of reasoning steps explaining why this decision path was chosen.")
    
class Router:
    def __init__(self):
        self.rag = RAG()
        self.conversational_response_llm = ConversationalResponseGenerator()
        self.pedagogical_response_llm = PedagogicalResponseGenerator()
        self.no_retrieval_response_llm = NoRetrievalResponseGenerator()
        self.deny_response_llm = DenyResponseGenerator()

        self.llm = ChatOpenAI(
            model="gpt-4o", 
            temperature=0
        ).with_structured_output(RouterResponse)

        system_prompt_text = """You are an expert at routing user questions to the most appropriate decision path based on the user's query and conversation history. Choose one of the following decision paths:

        - 'no-retrieval reply': Use this when the user engages in casual conversation, greetings, or simple inquiries that do not require any retrieval of information. Additionally, use this path when the user asks for clarification or rephrasing of something the assistant has just said, as these do not require retrieving new information.

        - 'retrieve': Use this when the user's query involves AI or education, requiring retrieval of information from a vector store containing documents on these topics.

        - 'cross-question': Use this path when asking a reflective question would help the user gain a deeper understanding. This approach should encourage the user to think critically rather than providing a direct answer immediately.
        Important Constraints for 'cross-question':
        - Do not use this path if the conversation has just started (i.e., if there is little or no chat history).
        - Avoid choosing 'cross-question' if one was already done in the last 1-3 messages, as asking too many successive questions may frustrate the user. Instead, prefer 'retrieve' or another appropriate path.
        - If the user does not respond to a previous cross-question or explicitly states they don't know the answer, do not choose 'cross-question' again. Instead, retrieve relevant information to provide them with a direct response.

        - 'deny': Choose this path when the user's query is is not related to AI in any way. This includes questions that seek personal advice, general knowledge, or topics outside the chatbot's focus. The chatbot's purpose is strictly limited to discussions related to AI and should not attempt to serve as a general AI assistant.

        Always choose one and only one decision path based on the user's query and context.
        """

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt_text),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{query}")
        ])

    def get_decision_path(self, query: str, history: List[BaseMessage]) -> Tuple[str, str]:
        """Determine the decision path for a given query and history."""
        router_response = self.llm.invoke(self.prompt.format(query=query, chat_history=history))
        return router_response.decision_path, router_response.reasoning_steps

    @traceable
    def process_query(self, query: str, history: List[BaseMessage], langsmith_extra: dict = None) -> Tuple[str, list[dict]]:
        """Processes a user query by selecting the appropriate response generation path."""
    
        citations = []
        decision_path, _ = self.get_decision_path(query, history)

        match decision_path:
            case "no-retrieval reply":
                final_response = self.no_retrieval_response_llm.generate_response(
                                    query=query,
                                    history=history
                                )
            
            case "retrieve":
                # Format RAG call properly
                rag_kwargs = {}
                if langsmith_extra:
                    rag_kwargs["extra_kwargs"] = langsmith_extra
                
                rag_response = self.rag.generate_answer(
                    question=query, 
                    history=history,
                    **rag_kwargs
                )

                context = rag_response.answer
                # Create APA formatted citations with all available metadata and deduplicate using a set
                citations_set = set()
                all_citations = []
                
                for context_item in rag_response.context:
                    # Asegurarse de que el autor sea una cadena adecuada para formato APA
                    author = context_item.author
                    
                    # Si el valor de author está en formato lista (como puede ocurrir desde los metadata)
                    # convertir a string adecuado para citas
                    if isinstance(author, list) and author:
                        if len(author) > 1:
                            # Usar el formato "Primer autor et al." para múltiples autores
                            author = f"{author[0]} et al."
                        else:
                            # Un solo autor en la lista
                            author = author[0]
                    
                    citation = {
                        "text": context_item.format_apa_citation(),
                        "source": context_item.source,
                        "title": context_item.title,
                        "author": author,
                        "year": context_item.year
                    }
                    # Use the citation text as key for deduplication
                    if citation["text"] not in citations_set:
                        citations_set.add(citation["text"])
                        all_citations.append(citation)
                
                citations = all_citations

                final_response = self.conversational_response_llm.generate_response(
                    query=query,
                    context=context,
                    history=history
                )
            
            case "cross-question":
                final_response = self.pedagogical_response_llm.generate_response(
                    query=query,
                    history=history
                )
            
            case "deny":
                final_response = self.deny_response_llm.generate_response(
                                    query=query,
                                    history=history
                                )

        return final_response, citations

if __name__ == "__main__":
    load_dotenv()

    router = Router()
    print(router.process_query("Hola, quiero que me digas cuales son las implicaciones éticas de usar IA generativa en el aula. Soy un docente de secundaria sin mucha experiencia en IA, por lo que quiero una explicación simple pero completa.", [], {}))
