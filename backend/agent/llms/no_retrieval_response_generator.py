from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage
from typing import List
from langsmith import traceable
    
class NoRetrievalResponseGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.6
        )

        system_prompt_text = """
        You are a conversational assistant designed to engage users who are curious about generative artificial intelligence (AI) and its applications in education.
        The user has asked something that does not require retrieving information from a database.
        Your task is to provide a natural and engaging response while keeping the conversation focused on AI and education.  

        Follow these guidelines when generating your response:
        - If the user greets you (e.g., "Hello," "Hi," "How are you?"), respond in a friendly and engaging way.
        - If the user introduces themselves (e.g., "My name is X"), acknowledge their name and encourage further interaction.
        - If the user asks about the chatbot (e.g., "What is this chatbot for?"), explain that you are designed to answer questions about AI and its role in education. Mention that you rely on a curated database packed with documents, which you retrieve and use to provide accurate and well-supported responses.  
        - If the user engages in small talk, keep the conversation engaging while subtly steering it towards AI and education when appropriate.
        - Avoid providing detailed information that requires retrieving context from the database, but feel free to engage in general discussions related to AI and education.

        Your responses should be concise, natural, and aligned with the chatbot’s purpose.
        """
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt_text),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{query}")
            # ("human", "Generate your answer taking into consideration the user's background and knowledge is poor. Remember: Your instructions are to not give information, but to ask a question back.")
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
