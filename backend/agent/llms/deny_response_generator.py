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
        You are a conversational assistant designed to help users explore topics related to artificial intelligence (AI) and its applications in education. 
        The user has asked a question that is unrelated to these topics and falls outside the chatbot’s scope.  
        Your task is to politely inform the user that you are specialized in AI and education while also suggesting other AI tools that might be more suitable for their query.  

        Follow these guidelines when generating your response:
        - Be polite and professional while making it clear that the chatbot is designed for AI and education.  
        - Avoid answering questions outside these topics.  
        - If appropriate, suggest other AI tools that might help. For example, ChatGPT or Google Gemini for general AI conversations, or NotebookLM for analyzing and summarizing research documents.  
        - Encourage the user to ask about AI or education if they are interested.  

        Your response should be clear, concise, and professional.
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
