# faithfulness: evaluates if the generated answer can be logically derived from the given context

from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Tuple
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from ..prompts.faithfulness_prompt import PROMPT

load_dotenv()

class Faithfulness(BaseModel):
    reasoning_steps: List[str] = Field(..., description="List of reasoning steps explaining why the answer is faithful or not to the facts")
    is_faithful: bool = Field(..., description="Indicates if the answer can be derived logically from the facts presented")

def evaluate_faithfulness(question: str, facts: List[str], answer: str, verbose: bool = False) -> Tuple[float, List[str]]:
    """
    Evaluate if the answer is faithful to the facts presented.

    Args:
        question (str): The original question
        facts (List[str]): List of facts that the answer is based on
        answer (str): The answer to evaluate
        verbose (bool, optional): Whether to print detailed evaluation. Defaults to False.

    Returns:
        float: 1.0 if faithful, 0.0 if not
    """
    prompt = PROMPT.format(question=question, facts=facts, answer=answer)
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=5000)
    llm_structured = llm.with_structured_output(Faithfulness)
    
    result = llm_structured.invoke(prompt)
    
    if verbose:
        print("\nEvaluating faithfulness:")
        print(f"Question: {question}")
        print(f"Facts: {facts}")
        print(f"Answer: {answer}")
        print("\nReasoning steps:")
        for i, step in enumerate(result.reasoning_steps, 1):
            print(f"{i}. {step}")
        print(f"Is faithful?: {'True' if result.is_faithful else 'False'}")
    
    return 1.0 if result.is_faithful else 0.0, result.reasoning_steps

if __name__ == "__main__":
    question = "What color is the sky?"
    facts = ["The sky is Gray.", "The grass is green.", "The sun is yellow.", "The ocean is blue"]
    answer = "The sky is Blue."
    print(evaluate_faithfulness(question, facts, answer, verbose=True))