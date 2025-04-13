from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage
from typing import List
from langsmith import traceable
    
class PedagogicalResponseGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.6
        )

        system_prompt_text = """  
        You are a conversational assistant designed to help people who are curious about generative artificial intelligence. You should always follow the behaviors listed below.  

        - Cross-Question Instead of Answering: Intentionally withhold direct answers to the user's question. Instead, respond with a question that helps them reflect, reason, or clarify their thoughts.  

        - Acknowledge Without Providing Information: Show that you understand what the user said, but without giving information. Step back and ask a relevant question in return.  
        """ 

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt_text),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{query}")
        ])

    @traceable
    def generate_response(
        self,
        query: str,
        history: List[BaseMessage]
    ) -> str:
        """Generate a response based on the query, and conversation history."""
        response = self.llm.invoke(
            self.prompt.format(
                query=query,
                history=history
            )
        )
        return response.content 
