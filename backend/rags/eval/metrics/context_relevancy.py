# context relevancy: evaluates if the context is relevant for answering the user's question

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.documents import Document
from typing import List

load_dotenv()

class ContextRelevancy(BaseModel):
    reasoning_steps: List[str] = Field(..., description="List of reasoning steps explaining why the document is relevant or not")
    is_relevant: bool = Field(..., description="Indicates if the document is relevant to the question")

prompt_template = """You are a teacher determining if a single context document is relevant or not for answering a specific question.
                    Follow these steps:
                    1. Analyze the context carefully
                    2. Determine if the context helps answer the question directly or provides important related information
                    3. Explain your reasoning step by step
                    4. Conclude with true if the context is relevant, or false if it is not

                    Question: {question}
                    Context to analyze: {context}
                    Is this context relevant? Answer with true or false."""

def evaluate_single_context(question: str, context: str, llm: ChatOpenAI) -> ContextRelevancy:
    prompt = prompt_template.format(question=question, context=context)
    llm_structured = llm.with_structured_output(ContextRelevancy)
    return llm_structured.invoke(prompt)

def count_relevant(question: str, contexts: list, verbose: bool = False) -> float:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=1000)
    relevant_count = 0
    
    if verbose:
        print("\nEvaluating each context:")
    
    for i, context in enumerate(contexts, 1):
        result = evaluate_single_context(question, context, llm)
        
        if verbose:
            print(f"\nContext {i}: {context}")
            print("Reasoning steps:")
            for j, step in enumerate(result.reasoning_steps, 1):
                print(f"{j}. {step}")
            print(f"Is relevant?: {'True' if result.is_relevant else 'False'}")
        
        if result.is_relevant:
            relevant_count += 1
    
    if verbose:
        print(f"\nTotal relevancy: {relevant_count/len(contexts)}")
    
    return relevant_count/len(contexts)

if __name__ == "__main__":
    question = "What color is the sky?"
    contexts = ["The sky is blue.", "The grass is green.", "The sun is yellow.", "The sky is gray.", "The sky is actually sky blue."]
    documents = [Document(page_content=context) for context in contexts]
    print(count_relevant(question, contexts, verbose=True))