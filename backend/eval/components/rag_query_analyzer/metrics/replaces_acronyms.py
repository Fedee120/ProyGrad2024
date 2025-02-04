from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import List
from ..prompts.replaces_acronyms_prompt import PROMPT

load_dotenv()

class ReplacesAcronyms(BaseModel):
    reasoning_steps: List[str] = Field(..., description="List of reasoning steps explaining if the acronyms were replaced correctly")
    is_correct: bool = Field(..., description="Indicates if the acronyms were replaced correctly according to expected output")

def evaluate_replaces_acronyms(
    original_query: str,
    generated_query: str,
    expected_query: str,
    verbose: bool = False
) -> float:
    """
    Evaluate if the query analyzer replaces acronyms correctly.

    Args:
        original_query (str): The original query with acronyms
        generated_query (str): The query produced by the analyzer
        expected_query (str): The expected query with correctly replaced acronyms
        verbose (bool, optional): Whether to print detailed evaluation. Defaults to False.

    Returns:
        float: 1.0 if acronyms were replaced correctly, 0.0 if not
    """
    prompt = PROMPT.format(
        original_query=original_query,
        generated_query=generated_query,
        expected_query=expected_query
    )
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=5000)
    llm_structured = llm.with_structured_output(ReplacesAcronyms)
    
    result = llm_structured.invoke(prompt)
    
    if verbose:
        print("\nEvaluating acronym replacement:")
        print(f"Original query: {original_query}")
        print(f"Generated query: {generated_query}")
        print(f"Expected query: {expected_query}")
        print("\nReasoning steps:")
        for i, step in enumerate(result.reasoning_steps, 1):
            print(f"{i}. {step}")
        print(f"Is correct?: {result.is_correct}")
    
    return 1.0 if result.is_correct else 0.0 