from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import List
from langchain_core.messages import AIMessage, HumanMessage
from ..prompts.resolves_references_prompt import PROMPT

load_dotenv()

class ResolvesReferences(BaseModel):
    reasoning_steps: List[str] = Field(..., description="List of reasoning steps explaining if the references were resolved correctly")
    is_correct: bool = Field(..., description="Indicates if the references were resolved correctly according to expected output")

def format_chat_history(messages: List[AIMessage | HumanMessage]) -> str:
    """Format chat history messages into a readable string."""
    formatted = []
    for msg in messages:
        role = "Human" if isinstance(msg, HumanMessage) else "Assistant"
        formatted.append(f"{role}: {msg.content}")
    return "\n".join(formatted)

def evaluate_resolves_references(
    original_query: str,
    generated_query: str,
    expected_query: str,
    chat_history: List[AIMessage | HumanMessage],
    verbose: bool = False
) -> float:
    """
    Evaluate if the query analyzer resolves references correctly.

    Args:
        original_query (str): The original query with references
        generated_query (str): The query produced by the analyzer
        expected_query (str): The expected query with correctly resolved references
        chat_history (List[AIMessage | HumanMessage]): The chat history messages
        verbose (bool, optional): Whether to print detailed evaluation. Defaults to False.

    Returns:
        float: 1.0 if references were resolved correctly, 0.0 if not
    """
    prompt = PROMPT.format(
        original_query=original_query,
        generated_query=generated_query,
        expected_query=expected_query,
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
        print(f"Generated query: {generated_query}")
        print(f"Expected query: {expected_query}")
        print("\nReasoning steps:")
        for i, step in enumerate(result.reasoning_steps, 1):
            print(f"{i}. {step}")
        print(f"Is correct?: {result.is_correct}")
    
    return 1.0 if result.is_correct else 0.0 