# context relevancy: evaluates if the context is relevant for answering the user's question

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.documents import Document
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..prompts.context_relevancy_prompt import PROMPT

load_dotenv()

class ContextRelevancy(BaseModel):
    reasoning_steps: List[str] = Field(..., description="List of reasoning steps explaining why the document is relevant or not")
    is_relevant: bool = Field(..., description="Indicates if the document is relevant to the question")

def evaluate_single_context(question: str, excerpt: str) -> Tuple[str, bool, List[str]]:
    """
    Evalúa un único contexto y retorna una tupla con el contexto, si es relevante y los pasos de razonamiento
    """
    prompt = PROMPT.format(question=question, excerpt=excerpt)
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=5000)
    llm_structured = llm.with_structured_output(ContextRelevancy)
    result = llm_structured.invoke(prompt)
    return excerpt, result.is_relevant, result.reasoning_steps

def evaluate_context_relevancy(
    question: str, 
    contexts: list, 
    max_workers: int = 3,
    verbose: bool = False
) -> float:
    """
    Evalúa múltiples contextos de forma concurrente y retorna la proporción de contextos relevantes
    
    Args:
        question: Pregunta a evaluar
        contexts: Lista de contextos
        max_workers: Número máximo de workers concurrentes
        verbose: Si se debe imprimir información detallada
    """
    relevant_count = 0
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Crear futures para cada contexto
        future_to_context = {
            executor.submit(evaluate_single_context, question, context): i 
            for i, context in enumerate(contexts, 1)
        }
        
        # Procesar resultados conforme se completan
        for future in as_completed(future_to_context):
            context_num = future_to_context[future]
            try:
                context, is_relevant, reasoning_steps = future.result()
                results.append((context_num, context, is_relevant, reasoning_steps))
                if is_relevant:
                    relevant_count += 1
                    
                if verbose:
                    print(f"\nContext {context_num}: {context}")
                    print("Reasoning steps:")
                    for j, step in enumerate(reasoning_steps, 1):
                        print(f"{j}. {step}")
                    print(f"Is relevant?: {is_relevant}")
                    
            except Exception as e:
                print(f"Error procesando contexto {context_num}: {str(e)}")
    
    relevancy_ratio = relevant_count/len(contexts)
    if verbose:
        print(f"\nTotal relevancy: {relevancy_ratio}")
    
    return relevancy_ratio

if __name__ == "__main__":
    question = "What color is the sky?"
    contexts = ["The sky is blue.", "The grass is green.", "The sun is yellow.", "The sky is gray.", "The sky is actually sky blue."]
    documents = [Document(page_content=context) for context in contexts]
    print(evaluate_context_relevancy(question, contexts, max_workers=4, verbose=True))