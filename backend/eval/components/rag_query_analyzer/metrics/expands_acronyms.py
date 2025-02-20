# expands_acronyms: evaluates if acronyms in the query are expanded in at least one generated query

from pydantic.v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import List, Tuple
from ..prompts.expands_acronyms_prompt import PROMPT

load_dotenv()

class ExpandsAcronyms(BaseModel):
    reasoning_steps: List[str] = Field(..., description="List of reasoning steps explaining if and how acronyms were expanded")
    has_expanded_acronyms: bool = Field(..., description="Indicates if acronyms (when present) are expanded in at least one query")

def evaluate_expands_acronyms(
    original_query: str,
    queries: List[str],
    verbose: bool = False
) -> Tuple[float, List[str]]:
    """
    Evaluate if acronyms in the original query are expanded in at least one of the generated queries.
    
    Args:
        original_query: The original query
        queries: List of generated queries
        verbose: Whether to print detailed evaluation information
        
    Returns:
        float: 1.0 if acronyms (when present) are expanded in at least one query, 0.0 if not
    """
    # Create prompt
    prompt = PROMPT.format(
        original_query=original_query,
        queries=queries
    )
    
    # Get structured output from LLM
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=5000)
    llm_structured = llm.with_structured_output(ExpandsAcronyms)
    result = llm_structured.invoke(prompt)
    
    if verbose:
        print("\nEvaluating acronym expansion:")
        print(f"Original query: {original_query}")
        print(f"Generated queries: {queries}")
        print("\nReasoning steps:")
        for i, step in enumerate(result.reasoning_steps, 1):
            print(f"{i}. {step}")
        print(f"Acronyms expanded?: {'True' if result.has_expanded_acronyms else 'False'}")
        
    return 1.0 if result.has_expanded_acronyms else 0.0, result.reasoning_steps

if __name__ == "__main__":
    query = "What is the difference between CNN and RNN?"
    queries = [
        "What is the difference between Convolutional Neural Network and Recurrent Neural Network?",
        "Compare CNN and RNN architectures",
        "CNN vs RNN main features"
    ]
    print(evaluate_expands_acronyms(query, queries, verbose=True)) 