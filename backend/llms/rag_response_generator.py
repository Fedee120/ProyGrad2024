from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List
from langsmith import traceable

class ContextItem(BaseModel):
    """A piece of context used to answer the question"""
    content: str = Field(description="The content of the context")
    source: str = Field(description="The name of the source that the context was retrieved from")

class ContextResponse(BaseModel):
    """Response format for question answering"""
    answer: str = Field(description="The answer to the question based on the provided context")
    context: List[ContextItem] = Field(description="List of context pieces that were actually used to form the answer, if it was not used do not return it")

class RAGResponseGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0
        ).with_structured_output(ContextResponse)

        self.prompt_template = """You are an assistant for question-answering tasks.
        Below you will find information you can use to answer the question.
        Use this information to provide a comprehensive answer.
        
        Question: {question}
        Information: {search_results}
        
        Remember:
        - Only use data from the provided information, never from your own knowledge
        - Think step by step making sure your answer is grounded in the provided information
        - If the information doesn't contain relevant data, return as your answer "No information found" with empty context
        """

        self.prompt = PromptTemplate(
            input_variables=["search_results", "question"],
            template=self.prompt_template,
        )

    @traceable
    def generate_response(self, question: str, search_results: str) -> ContextResponse:
        """Generate an answer based on the search results."""
        return self.llm.invoke(
            self.prompt.format(
                question=question,
                search_results=search_results
            )
        ) 