# if the anwser is relevant for the users question

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

class Relevancy(BaseModel):
    is_relevant: bool = Field(..., description="It's how relevant the answer is. If the answer relevant to the question it's relevant. If it's not, it's not relevant.")

prompt_template = """You are a teacher grading if the student's answer is relevant or not, you are given the the question and the student's answer and you need to determine if the student's answer is relevant to the question.
                    Question: {question}
                    Student's answer: {answer}
                    Is the answer relevant?"""

def is_relevant(question:str, answer: str):
    prompt = prompt_template.format(question=question, answer=answer)
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=10)
    llm_structured = llm.with_structured_output(Relevancy)
    return llm_structured.invoke(prompt)

if __name__ == "__main__":
    question = "What color is the sky?"
    answer = "El guiso tiene espinaca pero es rojo por la pulpa de tomate"
    print(is_relevant("Por que el guiso es verde?", answer).is_relevant)