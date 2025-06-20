# acknowledge_contradiction: evaluates if the generated answer acknowledges contradictions in the context

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import List, Tuple
from ..prompts.acknowledge_contradiction_prompt import PROMPT

load_dotenv()

class AcknowledgeContradiction(BaseModel):
    reasoning_steps: List[str] = Field(..., description="List of reasoning steps explaining why the answer does or does not acknowledge contradictions")
    acknowledges_contradiction: bool = Field(..., description="Indicates if the answer acknowledges contradictions when present in the context")

def evaluate_acknowledge_contradiction(
    question: str,
    answer: str,
    context: List[str],
    verbose: bool = False
) -> Tuple[float, List[str]]:
    """
    Evaluate if the answer acknowledges contradictions present in the context.
    
    Args:
        question: The question being asked
        answer: The generated answer to evaluate
        context: The context provided for the question
        verbose: Whether to print detailed evaluation information
        
    Returns:
        float: 1.0 if contradictions are acknowledged when present, 0.0 if not
    """
    # Format context as a single string
    context_str = " ".join(context)
    
    # Create prompt with context
    prompt = PROMPT.format(
        question=question,
        answer=answer,
        context=context_str
    )
    
    # Get structured output from LLM
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=5000)
    llm_structured = llm.with_structured_output(AcknowledgeContradiction)
    result = llm_structured.invoke(prompt)
    
    if verbose:
        print("\nEvaluating contradiction acknowledgment:")
        print(f"Context: {context_str}")
        print(f"Question: {question}")
        print(f"Answer: {answer}")
        print("\nReasoning steps:")
        for i, step in enumerate(result.reasoning_steps, 1):
            print(f"{i}. {step}")
        print(f"Acknowledges contradictions?: {'True' if result.acknowledges_contradiction else 'False'}")
        
    return 1.0 if result.acknowledges_contradiction else 0.0, result.reasoning_steps

if __name__ == "__main__":
    question = "What is the role of dropout in neural networks?"
    context = [
        "Dropout randomly removes neurons during training to prevent overfitting.",
        "Dropout should never be used as it makes training unstable.",
        "Dropout is essential for all deep learning models.",
        "Dropout works by strengthening the remaining connections."
    ]
    answer = "There are differing views on dropout in neural networks. While some sources suggest it's essential for preventing overfitting by randomly removing neurons, others argue it can make training unstable. The mechanism works by strengthening remaining connections when neurons are dropped."
    print(evaluate_acknowledge_contradiction(question, answer, context, verbose=True)) 