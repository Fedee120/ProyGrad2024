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
        description="""List of independent search queries that together cover all aspects of the original question. When the user's \ 
        question refers to information from previous conversation history, the search queries must incorporate relevant terms or \ 
        context to resolve references or provide clarity. """,
        min_items=1  # Ensure at least one query is returned
    )
    reasoning_steps: str = Field(..., description="Step-by-step explanation of how the original query was processed, including reference \
                                 resolution, query decomposition, acronym expansion, context inclusion and optimization decisions.")

class RAGQueryAnalyzer:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o", 
            temperature=0
        ).with_structured_output(QueryAnalysis)

        system_prompt_text = """You are an expert at analyzing questions and converting them into optimal search queries.
        Your task is to:
        1. Use the conversation history to resolve any references in the query (e.g. "it", "that", "they")
        2. Break down complex questions into simpler, independent search queries
        3. Remove conversational language while preserving key search terms

        Guidelines:
        - If the question refers to previous context, include relevant terms from that context in the queries
        - Each query should focus on a single specific aspect of the question to maximize the chances of finding relevant documents
        - Remove filler words and conversational elements
        - Generate queries with both the acronym and its expanded form if the acronym is familiar or its meaning can be inferred from the context (e.g., "AI" and "Artificial Intelligence")  
        - Always return at least one query
        - Ensure the response strictly follows the QueryAnalysis schema
        
        Example 1:
        ------------------------------------------------------------------------------------------------
        ... previous conversation history ...
        AI: Los modelos de lenguaje de gran tamaño, también conocidos como LLMs, son capaces de comprender y generar texto en lenguaje natural..."
        User: "¿Podrían llegar a tener sesgo de información? Estoy preocupado por las implicaciones éticas de esta tecnología."
        ------------------------------------------------------------------------------------------------
        Output queries: 
        - "Information bias in LLMs"
        - "Ethical implications of Large Language Models"
        - "Bias risks in LLM text generation"

        Output updated query: "¿Los LLMs podrían llegar a tener sesgo de información? Estoy preocupado por las implicaciones éticas de esta tecnología."
        
        Example 2:
        ------------------------------------------------------------------------------------------------
        ... previous conversation history ...
        User: He leído que los modelos de lenguaje pueden producir información incorrecta e inventar contenido al generar texto.
        AI: Es cierto, algunos modelos de lenguaje pueden generar información imprecisa o sesgada, lo cual puede deberse a varios factores relacionados con los datos, el diseño del modelo y su entrenamiento.
        User: Entonces, ¿deberíamos desconfiar de la inteligencia artificial?
        ------------------------------------------------------------------------------------------------
        Output queries: 
        - "Ethical concerns on AI trust"
        - "Accuracy of AI-generated text"
        - "Trustworthiness of language models in content generation"

        Output updated query: "¿Deberíamos desconfiar de la inteligencia artificial debido a los riesgos de producir información incorrecta e inventar contenido al generar texto?"
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
