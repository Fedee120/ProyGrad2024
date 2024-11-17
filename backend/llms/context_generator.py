from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List

class ContextItem(BaseModel):
    """A piece of context used to answer the question"""
    content: str = Field(description="The content of the context")
    source: str = Field(description="The name of the source that the context was retrieved from")

class ContextResponse(BaseModel):
    """Response format for question answering"""
    answer: str = Field(description="The answer to the question based on the provided context")
    context: List[ContextItem] = Field(description="List of context pieces that were actually used to form the answer, if it was not used do not return it")

class ContextGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0
        ).with_structured_output(ContextResponse)

        self.prompt_template = """You are an assistant for question-answering tasks.
        Below you will find multiple search results for different aspects of the user's question.
        Use these search results to provide a comprehensive answer.
        
        Question: {question}
        Context: {search_results}
        
        Remember:
        - Only use information from the provided search results
        - If search results don't contain relevant information, say "No information found"
        - Be clear about which parts of your answer come from which search results
        - Maintain accuracy while being helpful
        """

        self.prompt = PromptTemplate(
            input_variables=["search_results", "question"],
            template=self.prompt_template,
        )

    def generate_context(self, question: str, search_results: str) -> ContextResponse:
        """Generate an answer based on the search results."""
        return self.llm.invoke(
            self.prompt.format(
                question=question,
                search_results=search_results
            )
        ) 