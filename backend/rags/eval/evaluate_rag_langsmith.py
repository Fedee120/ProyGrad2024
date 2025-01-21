import json
from rags.eval.metrics.answer_correctness import evaluate_answer_correctness
from rags.eval.metrics.faithfulness import evaluate_faithfulness
from rags.eval.metrics.answer_relevancy import evaluate_answer_relevancy
from rags.eval.metrics.context_relevancy import evaluate_context_relevancy
from langsmith import Client
import os
from dotenv import load_dotenv
from rags.openai.rag import RAG
from datetime import datetime
from typing import List, Dict

load_dotenv()

# Constante para el nombre del dataset
DATASET_NAME = "RAG_Evaluation"

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
    rag = RAG(
        URI=os.getenv("MILVUS_STANDALONE_URL"),
        COLLECTION_NAME="real_collection",
        search_kwargs={"k": 10},
        search_type="mmr",
        embeddings_model_name="text-embedding-3-small"
    )
    question = inputs["question"]
    history = []
    answer = rag.generate_answer(question, history)
    return {
        "answer": answer.answer,
        "context": [doc.content for doc in answer.context]
    }


def evaluate_faithfulness_metric(
    inputs: dict, outputs: dict, reference_outputs: dict = None
) -> float: 
        question = inputs["question"]
        answer = outputs["answer"]
        context = outputs["context"]

        score = evaluate_faithfulness(question, context, answer)
        return score

def evaluate_answer_relevancy_metric(
    inputs: dict, outputs: dict, reference_outputs: dict = None
) -> float:
    question = inputs["question"]
    answer = outputs["answer"]

    score = evaluate_answer_relevancy(question, answer)
    return score

def evaluate_context_relevancy_metric(
    inputs: dict, outputs: dict, reference_outputs: dict = None
) -> float:
    question = inputs["question"]
    context = outputs["context"]

    score = evaluate_context_relevancy(question, context)
    return score

def evaluate_answer_correctness_metric(
    inputs: dict, outputs: dict, reference_outputs: dict = None
) -> float:
    """Evalúa la precisión de la respuesta comparada con la referencia, si existe."""
    if not reference_outputs or "ground_truth" not in reference_outputs:
        return 0.0  # No hay ground_truth

    question = inputs["question"]
    answer = outputs["answer"]
    reference_answer = reference_outputs["ground_truth"]

    score = evaluate_answer_correctness(question, answer, reference_answer)
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

def run_evaluation(
    metadata: Dict = {"version": "Query Analysis, gpt-4o evaluator"},
    dataset_name: str = DATASET_NAME,
    experiment_prefix: str = "RAG_System_Evaluation"
):
    # Obtener variables de entorno
    environment = os.getenv("ENVIRONMENT", "develop")
    developer = os.getenv("DEVELOPER", "unknown")
    
    # Actualizar el nombre del dataset con el ambiente
    dataset_name = f"{dataset_name}_{environment}"
    
    # Actualizar metadata con el desarrollador
    metadata.update({"developer": developer})
    
    # Inicializar el cliente y el sistema RAG
    client = Client()

    # Cargar dataset y preparar la evaluación
    examples = load_dataset()
    
    # Buscar si el dataset ya existe
    existing_datasets = client.list_datasets()
    dataset = next((ds for ds in existing_datasets if ds.name == dataset_name), None)
    
    if dataset is None:
        # Si no existe, crear el dataset
        dataset = client.create_dataset(
            dataset_name, 
            description=f"Dataset para evaluación de sistema RAG en ambiente {environment}"
        )
        
        # Crear ejemplos solo si el dataset es nuevo
        client.create_examples(
            inputs=[{"question": example["question"]} for example in examples],
            outputs=[{"ground_truth": example["ground_truth"]} for example in examples],
            dataset_id=dataset.id
        )
    
    # Ejecutar evaluación
    experiment_results = client.evaluate(
        target_function,
        data=dataset_name,
        evaluators=[
            evaluate_faithfulness_metric,
            evaluate_answer_relevancy_metric,
            evaluate_context_relevancy_metric,
            evaluate_answer_correctness_metric
        ],
        max_concurrency = len(examples),
        experiment_prefix=experiment_prefix,
        metadata=metadata,
    )

if __name__ == "__main__":
    run_evaluation()