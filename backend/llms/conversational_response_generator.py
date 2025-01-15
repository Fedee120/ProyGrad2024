from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage
from typing import List
from agent.prompt.prompt_v5 import PROMPT, AI_FOCUSED_BEHAVIOR, LANGUAGE_BEHAVIOR, GROUNDED_BEHAVIOR, CONVERSATIONAL_BEHAVIOR
from langsmith import traceable

class ConversationalResponseGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.6
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", f'''{PROMPT}
             -{AI_FOCUSED_BEHAVIOR} 
             -{LANGUAGE_BEHAVIOR} 
             -{GROUNDED_BEHAVIOR} 
             -{CONVERSATIONAL_BEHAVIOR} 
            ''' +
            '''
            ----------------------------------- Context Start -----------------------------------
            {context}
            ----------------------------------- Context End -----------------------------------
            '''),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{query}"),
            ("human", "Generate a helpful response based on the above context and conversation history. Remember: Your role is to be accurate and helpful while strictly adhering to the information provided by the context filter")
        ])

    @traceable
    def generate_response(
        self,
        query: str,
        context: str,
        history: List[BaseMessage]
    ) -> str:
        """Generate a response based on the query, context, and conversation history."""
        response = self.llm.invoke(
            self.prompt.format(
                query=query,
                context=context,
                history=history
            )
        )
        return response.content 