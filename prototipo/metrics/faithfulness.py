# faithfullness: the degree to which the answer is derived from the context.

from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

class Faithfulness(BaseModel):
    is_faithful: bool = Field(..., description="If the answer can be derived logically from the facts presented.")

prompt_template = """You are a teacher grading a student's answer. The student has presented a list of facts for an answer and you need to determine if the answer he gave is logicaly based on those facts or if it's not.
                    Question: {question}
                    Facts: {facts}
                    Answer: {answer}
                    Is the answer faithful?"""

def is_faithfull(question:str, facts: List[str], answer: str) -> Faithfulness:
    """
    Evaluate if the answer is faithful to the facts presented.

    :param facts: List of facts that the answer is based on.
    :param answer: The answer to evaluate.
    :return: Faithfulness object with the evaluation.
    """
    prompt = prompt_template.format(question=question, facts=facts, answer=answer)
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=10)
    llm_structured = llm.with_structured_output(Faithfulness)

    return llm_structured.invoke(prompt)

if __name__ == "__main__":
    question = "What color is the sky?"
    facts = ["The sky is Gray.", "The grass is green.", "The sun is yellow.", "The ocean is blue"]
    answer = "The sky is Blue."
    print(is_faithfull(question, facts, answer).is_faithful)