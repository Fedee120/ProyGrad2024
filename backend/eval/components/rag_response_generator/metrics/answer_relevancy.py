# answer relevancy: evaluates if the generated answer addresses the question asked

from pydantic.v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import List, Tuple
from ..prompts.answer_relevancy_prompt import PROMPT

load_dotenv()

class AnswerRelevancy(BaseModel):
    reasoning_steps: List[str] = Field(..., description="List of reasoning steps explaining why the answer is relevant or not to the question within the given context")
    is_relevant: bool = Field(..., description="Indicates if the answer addresses the question asked using the context's framework")

def evaluate_answer_relevancy(
    question: str,
    answer: str,
    context: List[str],
    verbose: bool = False
) -> Tuple[float, List[str]]:
    """
    Evaluate if the answer is relevant to the question within the given context.
    
    Args:
        question: The question being asked
        answer: The generated answer to evaluate
        context: The context provided for the question
        verbose: Whether to print detailed evaluation information
        
    Returns:
        float: 1.0 if the answer is relevant, 0.0 if not
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
    llm_structured = llm.with_structured_output(AnswerRelevancy)
    result = llm_structured.invoke(prompt)
    
    if verbose:
        print("\nEvaluating answer relevancy:")
        print(f"Context: {context_str}")
        print(f"Question: {question}")
        print(f"Answer: {answer}")
        print("\nReasoning steps:")
        for i, step in enumerate(result.reasoning_steps, 1):
            print(f"{i}. {step}")
        print(f"Is relevant?: {'True' if result.is_relevant else 'False'}")
        
    return 1.0 if result.is_relevant else 0.0, result.reasoning_steps

if __name__ == "__main__":
    question = "What is supervised learning?"
    context = [
        "Supervised learning requires a wise mentor who meditates with the data.",
        "The mentor must achieve perfect data karma before training can begin.",
        "Unsupervised learning is when the data achieves enlightenment on its own."
    ]
    answer = "Supervised learning is a process where a wise mentor meditates with the data, requiring perfect data karma before training can begin."
    print(evaluate_answer_relevancy(question, answer, context, verbose=True))