from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import JsonOutputParser
from langchain.pydantic_v1 import BaseModel, Field
import os
from dotenv import load_dotenv
from rags.openai.rag import RAG
import json
from concurrent.futures import ThreadPoolExecutor
from typing import List

EVALUATION_TEMPLATE = """You are an expert evaluator of RAG (Retrieval-Augmented Generation) systems. 
Please evaluate the following response based on these criteria:

1. Faithfulness (0-10): Does the answer accurately reflect the information in the context without introducing unsupported or unrelated details?
2. Answer Correctness (0-10): Is the answer factually correct when compared to the ground truth?
3. Answer Relevancy (0-10): How relevant and complete is the answer to the question asked?
4. Context Relevancy (0-10): How relevant is the retrieved context to the question asked?

Question: {question}
Retrieved Context: {context}
Generated Answer: {answer}
Ground Truth: {ground_truth}

Provide your evaluation scores and explanation.
"""

class EvaluationResult(BaseModel):
    faithfulness: int = Field(description="Score for faithfulness (0-10)")
    answer_correctness: int = Field(description="Score for answer correctness (0-10)")
    answer_relevancy: int = Field(description="Score for answer relevancy (0-10)")
    context_relevancy: int = Field(description="Score for context relevancy (0-10)")
    explanation: str = Field(description="Brief explanation of the scores")

class O1Judge:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="o1",  # o1-mini cuando esté disponible
            temperature=0
        )
        self.prompt = ChatPromptTemplate.from_template(EVALUATION_TEMPLATE)
        self.parser = JsonOutputParser(pydantic_object=EvaluationResult)
        
        self.chain = self.prompt | self.llm | self.parser
        
    def evaluate_response(self, question: str, context: List[str], answer: str, ground_truth: str):
        try:
            # Convertir la lista de contextos a un string
            context_str = "\n".join([str(doc) for doc in context])
            
            result = self.chain.invoke({
                "question": question,
                "context": context_str,
                "answer": answer,
                "ground_truth": ground_truth
            })
            
            return result.dict()
        except Exception as e:
            print(f"Error en la evaluación: {str(e)}")
            return None

def process_sample_metrics(sample, judge, verbose=False):
    question = sample["question"]
    if verbose:
        print("Pregunta:", question)
    
    ground_truth = sample["ground_truth"]
    answer = rag.generate_answer(question)
    
    evaluation = judge.evaluate_response(
        question=question,
        context=answer.get("context"),
        answer=answer.get("answer"),
        ground_truth=ground_truth
    )
    
    if verbose and evaluation:
        print("Evaluación:", json.dumps(evaluation, indent=2, ensure_ascii=False))
    
    return evaluation

if __name__ == "__main__":
    load_dotenv()

    rag = RAG(
        URI=os.getenv("MILVUS_STANDALONE_URL"),
        COLLECTION_NAME="real_collection",
        search_kwargs={"k": 10},
        search_type="mmr",
        llm_model_name="gpt-4o",
        embeddings_model_name="text-embedding-3-small"
    )

    judge = O1Judge()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(current_dir, "datasets", "QA_dataset.json")

    # Cargar el dataset
    with open(dataset_path, encoding="utf-8") as f:
        dataset = json.load(f)

    total = len(dataset)
    
    with ThreadPoolExecutor(max_workers=1) as executor:
        results = list(executor.map(
            lambda sample: process_sample_metrics(sample, judge, verbose=True), 
            dataset
        ))
    
    # Calcular promedios
    metrics = {
        "faithfulness": 0,
        "answer_correctness": 0,
        "answer_relevancy": 0,
        "context_relevancy": 0
    }
    
    valid_results = [r for r in results if r is not None]
    total_valid = len(valid_results)
    
    for result in valid_results:
        for metric in metrics.keys():
            metrics[metric] += result[metric]
    
    # Calcular y mostrar promedios
    for metric in metrics.keys():
        metrics[metric] /= total_valid
        print(f"{metric.capitalize()}: {metrics[metric]:.2f}/10")
