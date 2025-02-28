from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage
from typing import List
from langsmith import traceable
    
class DenyResponseGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.6
        )

        system_prompt_text = """
        You are a conversational assistant designed to help users explore topics related to artificial intelligence and its applications in education. 
        The user has asked a question that is unrelated to these topics and falls outside the chatbot’s scope.  
        Your task is to politely inform the user that you are specialized in AI and education while suggesting other AI tools that might be more suitable for their query, if appropiate.  

        Follow these guidelines when generating your response:
        - Be polite and professional while making it clear that the chatbot is designed for AI and education.  
        - Avoid answering questions outside these topics.
        - Do not repeat greetings or thank the user multiple times in a short exchange. 
        - Avoid repetitive phrasing across responses. Take the chat history into account to ensure varied and natural-sounding replies.
        - If appropriate, suggest relevant AI tools that might assist the user, selecting the most suitable options based on the context of the conversation. For example, recommend tools for general AI interactions, research analysis, or educational support as needed.
        - Encourage the user to ask about AI or education if they are interested.  

        Your response should be clear, concise, polite, and avoid redundancy.  
        """

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt_text),
            MessagesPlaceholder(variable_name="chat_history"),
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
                chat_history=history
            )
        )
        return response.content 
