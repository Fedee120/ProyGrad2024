# citations_real_and_used: evaluates if citations in the answer are real and properly used

from pydantic.v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import List, Dict
from ..prompts.citations_real_and_used_prompt import PROMPT

load_dotenv()

class CitationsRealAndUsed(BaseModel):
    reasoning_steps: List[str] = Field(..., description="List of reasoning steps explaining why the citations are or are not real and properly used")
    all_citations_valid: bool = Field(..., description="Indicates if all citations are both real and properly used")

def evaluate_citations_real_and_used(
    question: str,
    answer: str,
    citations: List[str],
    context: List[str],
    verbose: bool = False
) -> float:
    """
    Evaluate if citations in the answer are real (present in context) and properly used.
    
    Args:
        question: The question being asked
        answer: The generated answer to evaluate
        citations: The citations in the answer
        context: The context provided for the question
        verbose: Whether to print detailed evaluation information
        
    Returns:
        float: 1.0 if all citations are real and properly used, 0.0 if not
    """
    # Format context as a single string
    context_str = " ".join(context)
    
    # Create prompt with context
    prompt = PROMPT.format(
        question=question,
        answer=answer,
        citations=citations,
        context=context_str
    )
    
    # Get structured output from LLM
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=5000)
    llm_structured = llm.with_structured_output(CitationsRealAndUsed)
    result = llm_structured.invoke(prompt)
    
    if verbose:
        print("\nEvaluating citations:")
        print(f"Context: {context_str}")
        print(f"Question: {question}")
        print(f"Answer: {answer}")
        print("\nReasoning steps:")
        for i, step in enumerate(result.reasoning_steps, 1):
            print(f"{i}. {step}")
        print(f"All citations valid?: {'True' if result.all_citations_valid else 'False'}")
        
    return 1.0 if result.all_citations_valid else 0.0

if __name__ == "__main__":
    question = "What are the benefits of transfer learning?"
    context = [
        "According to a 2020 study, transfer learning reduces training time by 60%.",
        "Research by Smith et al. shows improved accuracy with pre-trained models.",
        "Transfer learning works well with limited data scenarios."
    ]
    answer = "According to the 2020 study, transfer learning significantly reduces training time by 60%. Smith et al.'s research demonstrates improved accuracy with pre-trained models. Some experts suggest it works well with limited datasets."
    print(evaluate_citations_real_and_used(question, answer, context, verbose=True)) 