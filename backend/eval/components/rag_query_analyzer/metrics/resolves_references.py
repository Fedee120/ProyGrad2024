from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import List, Tuple
from langchain_core.messages import AIMessage, HumanMessage
from ..prompts.resolves_references_prompt import PROMPT

load_dotenv()

class ResolvesReferences(BaseModel):
    reasoning_steps: List[str] = Field(..., description="List of reasoning steps explaining if the references were resolved correctly")
    resolves_references_correctly: bool = Field(..., description="Indicates if the references were resolved correctly according to expected output")

def format_chat_history(messages: List[AIMessage | HumanMessage]) -> str:
    """Format chat history messages into a readable string."""
    formatted = []
    for msg in messages:
        role = "Human" if isinstance(msg, HumanMessage) else "Assistant"
        formatted.append(f"{role}: {msg.content}")
    return "\n".join(formatted)

def evaluate_resolves_references(
    original_query: str,
    updated_query: str,
    queries: List[str],
    chat_history: List[AIMessage | HumanMessage],
    verbose: bool = False
) -> Tuple[float, List[str]]:
    """
    Evaluate if the query analyzer resolves references correctly.

    Args:
        original_query (str): The original query with references
        updated_query (str): The query produced by the analyzer
        queries (List[str]): The generated queries
        chat_history (List[AIMessage | HumanMessage]): The chat history messages
        verbose (bool, optional): Whether to print detailed evaluation. Defaults to False.

    Returns:
        float: 1.0 if references were resolved correctly, 0.0 if not
    """
    prompt = PROMPT.format(
        original_query=original_query,
        updated_query=updated_query,
        queries=queries,
        chat_history=format_chat_history(chat_history)
    )
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=5000)
    llm_structured = llm.with_structured_output(ResolvesReferences)
    
    result = llm_structured.invoke(prompt)
    
    if verbose:
        print("\nEvaluating reference resolution:")
        print("Chat History:")
        print(format_chat_history(chat_history))
        print(f"\nOriginal query: {original_query}")
        print(f"Updated query: {updated_query}")
        print(f"Generated queries: {queries}")
        print("\nReasoning steps:")
        for i, step in enumerate(result.reasoning_steps, 1):
            print(f"{i}. {step}")
        print(f"Is correct?: {result.resolves_references_correctly}")
    
    return 1.0 if result.resolves_references_correctly else 0.0, result.reasoning_steps