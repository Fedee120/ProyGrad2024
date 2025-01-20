# answer relevancy: evaluates if the generated answer addresses the question asked

from pydantic.v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import List

load_dotenv()

class AnswerRelevancy(BaseModel):
    reasoning_steps: List[str] = Field(..., description="List of reasoning steps explaining why the answer is relevant or not to the question")
    is_relevant: bool = Field(..., description="Indicates if the answer addresses the question asked")

prompt_template = """You are a teacher determining if a student's answer is relevant to the question asked.
                    Follow these steps:
                    1. Analyze the question carefully
                    2. Review the answer and its relationship to the question
                    3. Explain your reasoning step by step
                    4. Conclude with true if the answer is relevant to the question, or false if it is not

                    Question: {question}
                    Answer: {answer}
                    Is the answer relevant? Answer with true or false."""

def evaluate_answer_relevancy(question: str, answer: str, verbose: bool = False) -> float:
    """
    Evaluate if the answer is relevant to the question asked.

    Args:
        question (str): The question asked
        answer (str): The answer to evaluate
        verbose (bool, optional): Whether to print detailed evaluation. Defaults to False.

    Returns:
        float: 1.0 if relevant, 0.0 if not
    """
    prompt = prompt_template.format(question=question, answer=answer)
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=1000)
    llm_structured = llm.with_structured_output(AnswerRelevancy)
    
    result = llm_structured.invoke(prompt)
    
    if verbose:
        print("\nEvaluating answer relevancy:")
        print(f"Question: {question}")
        print(f"Answer: {answer}")
        print("\nReasoning steps:")
        for i, step in enumerate(result.reasoning_steps, 1):
            print(f"{i}. {step}")
        print(f"Is relevant?: {'True' if result.is_relevant else 'False'}")
    
    return 1.0 if result.is_relevant else 0.0

if __name__ == "__main__":
    question = "¿Cuál es la capital de Francia?"
    answer = "París es la capital de Francia y es conocida como la Ciudad de la Luz."
    print(evaluate_answer_relevancy(question, answer, verbose=True))