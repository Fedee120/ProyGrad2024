# groundedness: evaluates if the generated answer aligns with the ground truth answer

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Groundedness(BaseModel):
    reasoning_steps: List[str] = Field(..., description="List of reasoning steps explaining why the answer is grounded or not against the ground truth")
    is_grounded: bool = Field(..., description="Indicates if the answer is correct in relation to the expected answer")

prompt_template = """You are a teacher grading if the student's answer is correct or not. You need to determine if the student's answer aligns with the ground truth.
                    Follow these steps:
                    1. Analyze the question and both answers carefully
                    2. Compare the student's answer with the ground truth
                    3. Explain your reasoning step by step
                    4. Conclude with true if the answer is grounded in the truth, or false if it deviates from it

                    Question: {question}
                    Student's answer: {answer}
                    Ground truth: {ground_truth}
                    Is the answer grounded? Answer with true or false."""

def evaluate_groundedness(question: str, answer: str, ground_truth: str, verbose: bool = False) -> float:
    """
    Evaluate if the answer is grounded against the ground truth.

    Args:
        question (str): The original question
        answer (str): The answer to evaluate
        ground_truth (str): The correct answer to compare against
        verbose (bool, optional): Whether to print detailed evaluation. Defaults to False.

    Returns:
        float: 1.0 if grounded, 0.0 if not
    """
    prompt = prompt_template.format(question=question, answer=answer, ground_truth=ground_truth)
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=1000)
    llm_structured = llm.with_structured_output(Groundedness)
    
    result = llm_structured.invoke(prompt)
    
    if verbose:
        print("\nEvaluating groundedness:")
        print(f"Question: {question}")
        print(f"Student's answer: {answer}")
        print(f"Ground truth: {ground_truth}")
        print("\nReasoning steps:")
        for i, step in enumerate(result.reasoning_steps, 1):
            print(f"{i}. {step}")
        print(f"Is grounded?: {'True' if result.is_grounded else 'False'}")
    
    return 1.0 if result.is_grounded else 0.0

if __name__ == "__main__":
    question = "¿Por qué el guiso es verde?"
    answer = "El guiso tiene espinaca pero es rojo por la pulpa de tomate"
    ground_truth = "El guiso es verde por la espinaca"
    print(evaluate_groundedness(question, answer, ground_truth, verbose=True))