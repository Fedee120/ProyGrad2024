from typing import List
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langsmith import traceable

class QueryAnalysis(BaseModel):
    """A list of optimized search queries and the updated original query."""
    updated_query: str = Field(
        description="The original user query after processing references and context"
    )
    queries: List[str] = Field(
        description="List of independent search queries that together cover all aspects of the original question",
        min_items=1  # Ensure at least one query is returned
    )

class QueryAnalyzer:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0
        ).with_structured_output(QueryAnalysis)

        system_prompt_text = """You are an expert at analyzing questions and converting them into optimal search queries.
        Your task is to:
        1. Use the conversation history to resolve any references in the query (e.g. "it", "that", "they")
        2. Break down complex questions into simpler, independent search queries
        3. Remove conversational language while preserving key search terms

        Guidelines:
        - Each query should focus on a single specific aspect of the question to maximize the chances of finding relevant documents
        - Preserve technical terms and acronyms exactly as written with the exception of evident spelling errors
        - Remove filler words and conversational elements
        - Always return at least one query
        - If the question refers to previous context, include relevant terms from that context in the queries
        
        Example:
        ------------------------------------------------------------------------------------------------
        ... previous conversation history ...
        AI: Un LLM, que significa Large Language Model o modelo de lenguaje de gran tamaño, es un tipo de modelo de inteligencia artificial..."
        User: "¿No terminan teniendo sesgo de información? estoy muy preocupado por las implicaciones éticas de esta nueva tecnología"
        ------------------------------------------------------------------------------------------------
        Output queries: 
        - "Information bias in LLMs"
        - "Ethical implications of LLMs"
        Output updated query: "¿Los LLMs no terminan teniendo sesgo de información? estoy muy preocupado por las implicaciones éticas de esta nueva tecnología"
        """
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt_text),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{query}")
        ])

    @traceable
    def analyze(
        self, 
        query: str, 
        history: List[BaseMessage]
    ) -> QueryAnalysis:
        """Analyze a query and return a list of optimized search queries."""
        return self.llm.invoke(
            self.prompt.format(query=query, history=history)
        )
