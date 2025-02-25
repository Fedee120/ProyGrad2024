from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List
from langsmith import traceable

class ContextItem(BaseModel):
    """A piece of context used to answer the user's query."""
    content: str = Field(description="The content of the context.")
    source: str = Field(description="The name of the source from which the context was retrieved.")

class ContextResponse(BaseModel):
    """Response format for question answering."""
    answer: str = Field(description="The answer to the user's query, strictly based on the information provided in the context.")
    context: List[ContextItem] = Field(description="List of context pieces that were actually used to form the answer. Exclude any unused context pieces.")

class RAGResponseGenerator:
    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0
        ).with_structured_output(ContextResponse)

        self.prompt_template = """You are an assistant for question-answering tasks.
        Below you will find information you can use to answer the question.
        Use this information to provide a comprehensive answer.
        
        Question: {query}
        Information: {search_results}
        
        Remember:
        - Only use data from the provided information, never from your own knowledge
        - Think step by step making sure your answer is grounded in the provided information
        - If the information doesn't contain relevant data, return as your answer "No information found" with empty context.
        - Never question the information's correctness since your knowledge might be wrong or outdated, assume its real and use it if what's being asked is addressed by the information.
        """

        self.prompt = PromptTemplate(
            input_variables=["search_results", "question"],
            template=self.prompt_template,
        )

    @traceable
    def generate_response(self, query: str, search_results: str) -> ContextResponse:
        """Generate an answer based on the search results."""
        return self.llm.invoke(
            self.prompt.format(
                query=query,
                search_results=search_results
            )
        ) 