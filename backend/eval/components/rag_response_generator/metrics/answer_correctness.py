# answer correctness: evaluates if the generated answer is correct against the ground truth
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import List, Tuple
from ..prompts.answer_correctness_prompt import PROMPT

load_dotenv()

class AnswerCorrectness(BaseModel):
    reasoning_steps: List[str] = Field(..., description="List of reasoning steps explaining why the answer is correct or not against the ground truth")
    answer_is_correct: bool = Field(..., description="Indicates if the answer is correct in relation to the expected answer")

def evaluate_answer_correctness(question: str, answer: str, ground_truth: str, verbose: bool = False) -> Tuple[float, List[str]]:
    """
    Evaluate if the answer is correct against the ground truth.

    Args:
        question (str): The original question
        answer (str): The answer to evaluate
        ground_truth (str): The correct answer to compare against
        verbose (bool, optional): Whether to print detailed evaluation. Defaults to False.

    Returns:
        float: 1.0 if correct, 0.0 if not
    """
    prompt = PROMPT.format(question=question, answer=answer, ground_truth=ground_truth)
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=5000)
    llm_structured = llm.with_structured_output(AnswerCorrectness)
    
    result = llm_structured.invoke(prompt)
    
    if verbose:
        print("\nEvaluating answer correctness:")
        print(f"Question: {question}")
        print(f"Student's answer: {answer}")
        print(f"Ground truth: {ground_truth}")
        print("\nReasoning steps:")
        for i, step in enumerate(result.reasoning_steps, 1):
            print(f"{i}. {step}")
        print(f"Is correct?: {'True' if result.answer_is_correct else 'False'}")
    
    return 1.0 if result.answer_is_correct else 0.0, result.reasoning_steps

if __name__ == "__main__":
    question = "¿Por qué el guiso es verde?"
    answer = "El guiso tiene espinaca pero es rojo por la pulpa de tomate"
    ground_truth = "El guiso es verde por la espinaca"
    print(evaluate_answer_correctness(question, answer, ground_truth, verbose=True)) 