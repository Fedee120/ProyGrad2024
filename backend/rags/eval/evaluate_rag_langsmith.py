import json
from rags.eval.metrics.groundedness import evaluate_groundedness
from rags.eval.metrics.faithfulness import evaluate_faithfulness
from rags.eval.metrics.answer_relevancy import evaluate_relevancy
from rags.eval.metrics.context_relevancy import count_relevant
from langsmith import Client
import os
from dotenv import load_dotenv
from rags.openai.rag import RAG
from datetime import datetime
from typing import List, Dict

load_dotenv()

client = Client()

rag = RAG(
    URI=os.getenv("MILVUS_STANDALONE_URL"),
    COLLECTION_NAME="real_collection",
    search_kwargs={"k": 10},
    search_type="mmr",
    embeddings_model_name="text-embedding-3-small"
)

def target_function(inputs: dict) -> dict:
    """Función que LangSmith evaluará."""
    question = inputs["question"]
    history = []
    answer = rag.generate_answer(question, history)
    return {
        "answer": answer.answer,
        "context": [doc.content for doc in answer.context]
    }


def evaluate_faithfulness_metric(
    inputs: dict, outputs: dict, reference_outputs: dict = None
) -> float:  # CAMBIO: Retornamos float
        question = inputs["question"]
        answer = outputs["answer"]
        context = outputs["context"]

        score = evaluate_faithfulness(question, context, answer)
        return score  # CAMBIO: Retorno float

def evaluate_answer_relevancy_metric(
    inputs: dict, outputs: dict, reference_outputs: dict = None
) -> float:  # CAMBIO: Retornamos float
    question = inputs["question"]
    answer = outputs["answer"]

    score = evaluate_relevancy(question, answer)
    return score  # CAMBIO: Retorno float

def evaluate_context_relevancy_metric(
    inputs: dict, outputs: dict, reference_outputs: dict = None
) -> float:
    question = inputs["question"]
    context = outputs["context"]

    score = count_relevant(question, context)
    return score

def evaluate_groundedness_metric(
    inputs: dict, outputs: dict, reference_outputs: dict = None
) -> float:
    """Evalúa la precisión de la respuesta comparada con la referencia, si existe."""
    if not reference_outputs or "ground_truth" not in reference_outputs:
        return 0.0  # No hay ground_truth

    question = inputs["question"]
    answer = outputs["answer"]
    reference_answer = reference_outputs["ground_truth"]

    score = evaluate_groundedness(question, answer, reference_answer)
    return score

def load_dataset() -> List[Dict]:
    """Carga el dataset desde el archivo JSON."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(current_dir, "datasets", "QA_dataset.json")

    try:
        with open(dataset_path, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return [{
            "question": "¿Cuáles son los principales componentes de un sistema RAG?",
            "ground_truth": "Los principales componentes de un sistema RAG son el retriever que busca documentos relevantes, el generador que produce respuestas basadas en el contexto, y la base de conocimientos que almacena la información."
        }]

# def load_dataset() -> List[Dict]:
#     """mock dataset"""
#     return [
#         {"question": "¿Cuáles son los principales componentes de un sistema RAG?", "ground_truth": "Los principales componentes de un sistema RAG son el retriever que busca documentos relevantes, el generador que produce respuestas basadas en el contexto, y la base de conocimientos que almacena la información."}
# ]

examples = load_dataset()

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
dataset_name = f"RAG_System_Evaluation_{timestamp}"
dataset = client.create_dataset(dataset_name, description="Dataset para evaluación de sistema RAG")
client.create_examples(
    inputs=[{"question": example["question"]} for example in examples],
    outputs=[{"ground_truth": example["ground_truth"]} for example in examples],
    dataset_id=dataset.id
)

experiment_results = client.evaluate(
    target_function,
    data=dataset_name,
    evaluators=[
        evaluate_faithfulness_metric,
        evaluate_answer_relevancy_metric,
        evaluate_context_relevancy_metric,
        evaluate_groundedness_metric
    ],
    max_concurrency = 57,
    experiment_prefix="RAG_System_Evaluation",
    metadata={"version": "Query expansion, gpt-4o evaluator"},
)