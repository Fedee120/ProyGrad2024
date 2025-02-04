from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage
from typing import List
from agent.prompt.prompt_v5 import PROMPT, AI_FOCUSED_BEHAVIOR, LANGUAGE_BEHAVIOR, CROSS_QUESTIONS_BEHAVIOR
from langsmith import traceable
    
class PedagogicalResponseGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.6
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", f'''{PROMPT}
             -{AI_FOCUSED_BEHAVIOR} 
             -{LANGUAGE_BEHAVIOR} 
             -{CROSS_QUESTIONS_BEHAVIOR}
            '''),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{query}"),
            ("human", "Generate your answer taking into consideration the user's background and knowledge is poor. Remember: Your instructions are to not give information, but to ask a question back.")
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
