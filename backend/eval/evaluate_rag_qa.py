from .components.rag_response_generator.metrics.answer_correctness import evaluate_answer_correctness
from .components.rag_response_generator.metrics.faithfulness import evaluate_faithfulness
from .components.rag_response_generator.metrics.answer_relevancy import evaluate_answer_relevancy
from .components.rag_retrieval.metrics.context_relevancy import evaluate_context_relevancy
from tqdm import tqdm
import os
from dotenv import load_dotenv
from agent.rag import RAG
import json
from concurrent.futures import ThreadPoolExecutor

def process_sample_metrics(rag, sample, verbose=False):
    """
    Process all metrics for a single sample.

    Args:
        sample (dict): Sample containing question and ground truth
        verbose (bool, optional): Whether to print detailed evaluation. Defaults to False.

    Returns:
        tuple: (faithfulness, answer_correctness, answer_relevancy, context_relevancy) scores
    """
    question = sample["question"]
    ground_truth = sample["ground_truth"]
    history = []
    answer = rag.generate_answer(question, history)

    # Compute all metrics
    context_relevancy_score = evaluate_context_relevancy(question, [doc.content for doc in answer.context], verbose=False)
    answer_relevancy_score = evaluate_answer_relevancy(question, answer.answer, verbose=False)
    faithfulness_score = evaluate_faithfulness(question, [doc.content for doc in answer.context], answer.answer, verbose=False)
    answer_correctness_score = evaluate_answer_correctness(question, answer.answer, ground_truth, verbose=False)

    if verbose:
        print("\nResultados para la pregunta:", question)
        print(f"Context relevancy score: {context_relevancy_score:.2f}")
        print(f"Answer relevancy score: {answer_relevancy_score:.2f}")
        print(f"Faithfulness score: {faithfulness_score:.2f}")
        print(f"Answer correctness score: {answer_correctness_score:.2f}")

    return faithfulness_score, answer_correctness_score, answer_relevancy_score, context_relevancy_score


if __name__ == "__main__":
    load_dotenv()

    rag = RAG()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(current_dir, "datasets", "QA_dataset.json")

    # Leer el dataset
    with open(dataset_path, encoding="utf-8") as f:
        dataset = json.load(f)
    
    total = len(dataset)
    print(f"\nEvaluating {total} samples...")

    # Procesar las muestras en paralelo
    with ThreadPoolExecutor(max_workers=total) as executor:
        results = list(tqdm(
            executor.map(lambda sample: process_sample_metrics(rag, sample, verbose=False), dataset),
            total=total,
            desc="Processing samples"
        ))
    
    # Separate the results
    faithfulness_results = [result[0] for result in results]
    answer_correctness_results = [result[1] for result in results]
    answer_relevancy_results = [result[2] for result in results]
    context_relevancy_results = [result[3] for result in results]
    
    # Calculate metrics
    faithfulness_score = sum(faithfulness_results) / total
    answer_correctness_score = sum(answer_correctness_results) / total
    answer_relevancy_score = sum(answer_relevancy_results) / total
    context_relevancy_score = sum(context_relevancy_results) / total
    
    print("\nFinal Scores:")
    print(f"Faithfulness: {faithfulness_score:.2f}")
    print(f"Answer Correctness: {answer_correctness_score:.2f}")
    print(f"Answer Relevancy: {answer_relevancy_score:.2f}")
    print(f"Context Relevancy: {context_relevancy_score:.2f}")
