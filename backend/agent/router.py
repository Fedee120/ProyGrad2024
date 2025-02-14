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
            model="gpt-4o-mini", 
            temperature=0
        ).with_structured_output(RouterResponse)

        system_prompt_text = """You are an expert at routing user questions to the most appropriate decision path based on
        the user's query and conversation history. Choose one of the following decision paths: 

        - 'no-retrieval reply': Use this when the user engages in casual conversation, greetings, or simple inquiries that 
        do not require any retrieval of information.\n

        - 'retrieve': Use this when the user's query involves AI or education, requiring retrieval of information from a 
        vector store containing documents on these topics.\n

        - 'cross-question': Use this path when asking a reflective question would help the user gain a deeper understanding.
        This approach should encourage the user to think critically rather than providing a direct answer immediately.\n

        - 'deny': Use this when the query is unrelated to AI or education. This path applies to questions outside the 
        chatbot's scope.

        Always choose one and only one decision path based on the user's query and context.
        """

        #emjemplos?
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt_text),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{query}")
        ])

    @traceable
    def process_query(self, query: str, history: List[BaseMessage]) -> Tuple[str, list[str], bool]:
        router_response = self.llm.invoke(self.prompt.format(query=query, history=history))
        match router_response.decision_path:
            case "no-retrieval reply":
                final_response = self.no_retrieval_response_llm.generate_response(
                                    query=query,
                                    history=history
                                )
            
            case "retrieve":
                rag_response = self.rag.generate_answer(query, history)

                context = rag_response.answer
                citations = [
                    context_item.source 
                    for context_item in rag_response.context
                ]

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
    print(router.process_query("Hola, quiero que me digas cuales son las implicaciones éticas de usar IA generativa en el aula. Soy un docente de secundaria sin mucha experiencia en IA, por lo que quiero una explicación simple pero completa.", []))
