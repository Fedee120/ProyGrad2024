from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import List
from ..prompts.splits_when_needed_prompt import PROMPT

load_dotenv()

class SplitsWhenNeeded(BaseModel):
    reasoning_steps: List[str] = Field(..., description="List of reasoning steps explaining if the query splitting was done correctly")
    is_correct: bool = Field(..., description="Indicates if the query was correctly split into multiple queries when needed")

def evaluate_splits_when_needed(
    original_query: str,
    generated_queries: List[str],
    expected_queries: List[str],
    verbose: bool = False
) -> float:
    """
    Evaluate if the query analyzer correctly decides when to split queries.

    Args:
        original_query (str): The original query
        generated_queries (List[str]): The queries produced by the analyzer
        expected_queries (List[str]): The expected queries after splitting
        verbose (bool, optional): Whether to print detailed evaluation. Defaults to False.

    Returns:
        float: 1.0 if query splitting decision was correct, 0.0 if not
    """
    prompt = PROMPT.format(
        original_query=original_query,
        generated_queries=generated_queries,
        expected_queries=expected_queries
    )
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=5000)
    llm_structured = llm.with_structured_output(SplitsWhenNeeded)
    
    result = llm_structured.invoke(prompt)
    
    if verbose:
        print("\nEvaluating query splitting:")
        print(f"Original query: {original_query}")
        print(f"Generated queries: {generated_queries}")
        print(f"Expected queries: {expected_queries}")
        print("\nReasoning steps:")
        for i, step in enumerate(result.reasoning_steps, 1):
            print(f"{i}. {step}")
        print(f"Is correct?: {result.is_correct}")
    
    return 1.0 if result.is_correct else 0.0 