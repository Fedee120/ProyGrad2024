from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List, Optional
from langsmith import traceable
import re

def extract_year_from_creation_date(creation_date: Optional[str]) -> Optional[str]:
    """
    Extract the year from a creation date string in format like 'D:20240607114253+02'00''.
    Returns None if the date is missing or invalid.
    """
    if not creation_date:
        return None
    
    # Try to extract the year (first 4 digits after 'D:')
    year_match = re.search(r'D:(\d{4})', creation_date)
    if year_match:
        return year_match.group(1)
    
    return None

class ContextItem(BaseModel):
    """A piece of context used to answer the user's query."""
    content: str = Field(description="The content of the context.")
    source: str = Field(description="The name of the source from which the context was retrieved.")
    title: Optional[str] = Field(None, description="The title of the document.")
    author: Optional[str] = Field(None, description="The author of the document.")
    year: Optional[str] = Field(None, description="The year the document was created.")
    
    def format_apa_citation(self) -> str:
        """
        Format the citation in APA style based on available information.
        Falls back gracefully when information is missing.
        - Usa 'et al.' cuando hay más de un autor
        - Maneja correctamente los formatos de año
        """
        # Handle missing title
        title = self.title if self.title else self.source
        
        # Handle authors with 'et al.' rule
        if not self.author:
            author = "Autor desconocido"
        else:
            # Verificar si es una lista de autores o una cadena con separadores
            if ',' in self.author:
                # Puede ser una cadena con varios autores separados por comas
                authors_list = [a.strip() for a in self.author.split(',')]
                if len(authors_list) > 1:
                    author = f"{authors_list[0]} et al."
                else:
                    author = self.author
            elif ';' in self.author:
                # Puede ser una cadena con varios autores separados por punto y coma
                authors_list = [a.strip() for a in self.author.split(';')]
                if len(authors_list) > 1:
                    author = f"{authors_list[0]} et al."
                else:
                    author = self.author
            elif ' y ' in self.author.lower() or ' and ' in self.author.lower():
                # Puede contener "y" o "and" indicando múltiples autores
                author = f"{self.author.split(' y ')[0].split(' and ')[0]} et al."
            else:
                # Un solo autor
                author = self.author
        
        # Format based on available information
        if self.year:
            return f"{author} ({self.year}). {title}."
        else:
            return f"{author} (s.f.). {title}."

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
        - When returning context items, be sure to include ALL available metadata (title, author, year) for proper citation formatting.
        - Each context item should contain the exact source from the metadata, as well as the title, author, and year when available.
        - When handling author fields, if the metadata contains 'authors' (plural), use that as the 'author' field in your response.
        - For multiple authors, convert the list to a comma-separated string, or keep the existing comma-separated format.
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