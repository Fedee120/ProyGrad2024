# if the anwser is relevant for the users question
# esta metrica deberia hacerse para cada contexto pero no tengo tiempo ahora para eso jajaja

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.documents import Document

load_dotenv()

class Relevancy(BaseModel):
    number_of_relevant: int = Field(..., description="It's how many of the context documents are relevant to the question.")

prompt_template = """You are a teacher grading if the student provided contexts are relevant or not, you are given the question and the student's contexts and you need to determine how many of the student's contexts are relevant to the question.
                    Question: {question}
                    Student's contexts: {contexts}
                    How many contexts are relevant?"""

def count_relevant(question:str, contexts: list):
    # get the page_content from the documents
    contexts_string = "\n\n".join(contexts)
    prompt = prompt_template.format(question=question, contexts=contexts_string)
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=10)
    llm_structured = llm.with_structured_output(Relevancy)
    return int(llm_structured.invoke(prompt).number_of_relevant)/len(contexts)

if __name__ == "__main__":
    question = "What color is the sky?"
    contexts = ["The sky is blue.", "The grass is green.", "The sun is yellow.", "The sky is gray.", "The sky is actually sky blue."]
    documents = [Document(page_content=context) for context in contexts]
    print(count_relevant(question, contexts))