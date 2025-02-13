# includes_context: evaluates if the query analyzer considers conversation context

from pydantic.v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import List, Tuple
from ..prompts.includes_context_prompt import PROMPT
from langchain.schema import AIMessage, HumanMessage

load_dotenv()

class IncludesContext(BaseModel):
    reasoning_steps: List[str] = Field(..., description="List of reasoning steps explaining if and how context was considered")
    includes_context: bool = Field(..., description="Indicates if the queries show consideration of conversation context")

def format_chat_history(messages: List[AIMessage | HumanMessage]) -> str:
    """Format chat history messages into a readable string."""
    formatted = []
    for msg in messages:
        role = "Human" if isinstance(msg, HumanMessage) else "Assistant"
        formatted.append(f"{role}: {msg.content}")
    return "\n".join(formatted)

def evaluate_includes_context(
    original_query: str,
    queries: List[str],
    updated_query: str,
    chat_history: List[AIMessage | HumanMessage],
    expected_queries: List[str],
    expected_updated_query: str,
    verbose: bool = False
) -> Tuple[float, List[str]]:
    """
    Evaluate if the analyzer considers conversation context when generating queries.
    
    Args:
        original_query: The original query from the user
        queries: List of generated queries
        updated_query: The expanded query that includes context
        chat_history: List of previous conversation messages
        expected_queries: List of expected queries for comparison
        expected_updated_query: The expected updated query for comparison
        verbose: Whether to print detailed evaluation information
        
    Returns:
        float: 1.0 if queries show consideration of context, 0.0 if not
    """
    prompt = PROMPT.format(
        original_query=original_query,
        queries=queries,
        updated_query=updated_query,
        chat_history=format_chat_history(chat_history),
        expected_queries=expected_queries,
        expected_updated_query=expected_updated_query
    )
    
    # Get structured output from LLM
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=5000)
    llm_structured = llm.with_structured_output(IncludesContext)
    result = llm_structured.invoke(prompt)
    
    if verbose:
        print("\nEvaluating context inclusion:")
        print(f"Chat history:")
        print(format_chat_history(chat_history))
        print(f"Original query: {original_query}")
        print(f"Expected queries: {expected_queries}")
        print(f"Generated queries: {queries}")
        print(f"Updated query: {updated_query}")
        print(f"Expected updated query: {expected_updated_query}")
        print("\nReasoning steps:")
        for i, step in enumerate(result.reasoning_steps, 1):
            print(f"{i}. {step}")
        print(f"Includes context?: {'True' if result.includes_context else 'False'}")
        
    return 1.0 if result.includes_context else 0.0, result.reasoning_steps
