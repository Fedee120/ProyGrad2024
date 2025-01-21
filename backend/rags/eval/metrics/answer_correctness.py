# answer correctness: evaluates if the generated answer is correct against the ground truth
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import List

load_dotenv()

class AnswerCorrectness(BaseModel):
    reasoning_steps: List[str] = Field(..., description="List of reasoning steps explaining why the answer is correct or not against the ground truth")
    is_correct: bool = Field(..., description="Indicates if the answer is correct in relation to the expected answer")

prompt_template = """You are a teacher grading whether a student's answer is correct. Your goal is to determine if the student's answer conceptually aligns with the ground truth.
                    Follow these steps:
                    1. Analyze the question, student's answer and ground truth
                    2. Compare the student's answer with the ground truth
                    3. Explain your reasoning step by step
                    4. Conclude with "true" if the student's answer conceptually matches the ground truth, or "false" if it does not.

                    Question: {question}
                    Student's answer: {answer}
                    Ground truth: {ground_truth}
                    Is the answer correct? Answer with true or false."""

def evaluate_answer_correctness(question: str, answer: str, ground_truth: str, verbose: bool = False) -> float:
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
    prompt = prompt_template.format(question=question, answer=answer, ground_truth=ground_truth)
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=1000)
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
        print(f"Is correct?: {'True' if result.is_correct else 'False'}")
    
    return 1.0 if result.is_correct else 0.0

if __name__ == "__main__":
    question = "¿Por qué el guiso es verde?"
    answer = "El guiso tiene espinaca pero es rojo por la pulpa de tomate"
    ground_truth = "El guiso es verde por la espinaca"
    print(evaluate_answer_correctness(question, answer, ground_truth, verbose=True)) 