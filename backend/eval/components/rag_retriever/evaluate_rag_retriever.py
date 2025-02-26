from agent.rag import RAG
from langchain_core.documents import Document
from data.splitters.semantic_splitter import semantic_split
from .metrics.context_relevancy import evaluate_context_relevancy
from .metrics.context_recall import evaluate_context_recall
import json
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Tuple

def _load_test_collection(rag: RAG, dataset: Dict[str, Any]) -> None:
    """Load test documents into a test collection."""
    
    # Delete any existing documents
    rag.delete_all_documents()
    
    # Convert test documents to Document objects
    documents = []
    for doc in dataset["test_documents"]:
        documents.append(Document(
            page_content=doc["content"],
            metadata=doc["metadata"]
        ))
    
    # Split documents into smaller chunks
    split_documents = semantic_split(documents)
    
    # Add test documents to collection
    rag.add_documents(split_documents)

def evaluate_retrieval_samples(
    rag: RAG,
    samples: List[Dict[str, Any]], 
    verbose: bool = False
) -> Tuple[List[float], List[Dict[str, Any]]]:
    """
    Evaluate retrieval test samples.
    
    Args:
        rag: The RAG instance to evaluate
        samples: List of test samples with queries and ground truth
        verbose: Whether to print detailed evaluation information
        
    Returns:
        Tuple[List[float], List[Dict[str, Any]]]: List of scores and detailed results
    """
    scores = []
    details = []
    
    def evaluate_single_sample(sample: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        # Get retriever's output using retrieve method
        retrieved_docs = rag.retrieve(sample["query"])
        retrieved_contexts = [doc.page_content for doc in retrieved_docs]
        
        # Ensure we have at least 1 worker
        num_workers = max(1, len(retrieved_contexts))
        
        # Evaluate context relevancy
        relevancy_score, relevancy_details = evaluate_context_relevancy(
            question=sample["query"],
            contexts=retrieved_contexts,
            verbose=verbose,
            max_workers=num_workers
        )
        
        # Evaluate context recall against ground truth
        recall_score, recall_details = evaluate_context_recall(
            query=sample["query"],
            contexts=retrieved_contexts,
            ground_truth=sample["ground_truth"],
            verbose=verbose,
            max_workers=num_workers
        )
        
        # Average the scores
        score = (relevancy_score + recall_score) / 2
        
        # Store test details
        test_details = {
            "query": sample["query"],
            "retrieved_contexts": retrieved_contexts,
            "ground_truth": sample["ground_truth"],
            "relevancy_score": relevancy_score,
            "relevancy_details": relevancy_details,
            "recall_score": recall_score,
            "recall_details": {
                "recall_score": recall_details["recall_score"],
                "weighted_recall_score": recall_details["weighted_recall_score"],
                "per_context_results": recall_details["per_context_results"],
                "total_ground_truth_statements": recall_details["total_statements"],
                "total_contexts": len(retrieved_contexts)
            },
            "score": score
        }

        if verbose:
            print(f"\nEvaluating retrieval for query: {sample['query']}")
            print(f"Retrieved contexts: {retrieved_contexts}")
            print(f"Ground truth: {sample['ground_truth']}")
            print(f"Relevancy score: {relevancy_score:.2f}")
            print(f"Recall score: {recall_score:.2f}")
            print(f"Overall score: {score:.2f}")

        return score, test_details
    
    # Process samples in parallel
    with ThreadPoolExecutor(max_workers=len(samples)) as executor:
        futures = [executor.submit(evaluate_single_sample, sample) for sample in samples]
        for future in futures:
            score, test_details = future.result()
            scores.append(score)
            details.append(test_details)
            
    return scores, details

def evaluate_rag_retriever(verbose: bool = False, test_mode: bool = False) -> Tuple[Dict[str, float], List[Dict[str, Any]]]:
    """
    Run evaluations for the RAG Retriever component.
    
    Args:
        verbose: Whether to print detailed evaluation information
        test_mode: Whether to use test documents (True) or real collection (False)
        
    Returns:
        Tuple[Dict[str, float], List[Dict[str, Any]]]: Dictionary mapping metric names to their scores,
        and list of detailed test results
    """
    load_dotenv()
    
    # Initialize RAG with appropriate collection
    rag = RAG(collection_name="test_collection", k=1) if test_mode else RAG()
    
    # Load appropriate dataset
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(
        current_dir, 
        "datasets", 
        "test_retrieval_dataset.json" if test_mode else "real_retrieval_dataset.json"
    )
    
    with open(dataset_path, encoding="utf-8") as f:
        dataset = json.load(f)
    
    # Only load test documents in test mode
    if test_mode:
        _load_test_collection(rag, dataset)
    
    # Evaluate retrieval
    scores, details = evaluate_retrieval_samples(
        rag=rag,
        samples=dataset["test_queries"],
        verbose=verbose
    )
    
    # Calculate average scores
    avg_score = sum(scores) / len(scores)
    avg_relevancy_best = sum(d["relevancy_details"]["relevancy_ratio_best"] for d in details) / len(details)
    avg_relevancy_all = sum(d["relevancy_details"]["relevancy_ratio_all"] for d in details) / len(details)
    
    # Access recall scores directly from recall_details dictionary
    avg_recall = sum(d["recall_details"]["recall_score_best"] for d in details) / len(details)
    avg_weighted_recall = sum(d["recall_details"]["recall_score_all"] for d in details) / len(details)
    
    # Prepare results
    scores_dict = {
        "Context Relevancy (with all contexts)": avg_relevancy_all,
        "Context Relevancy (with best context)": avg_relevancy_best,
        "Context Recall": avg_recall,
        "Weighted Context Recall": avg_weighted_recall,
        "Overall": avg_score
    }
    
    if verbose:
        print("\nFinal Scores:")
        print(f"Context Relevancy (best): {avg_relevancy_best:.2f}")
        print(f"Context Relevancy (all): {avg_relevancy_all:.2f}")
        print(f"Context Recall: {avg_recall:.2f}")
        print(f"Weighted Context Recall: {avg_weighted_recall:.2f}")
        print(f"Overall Score: {avg_score:.2f}")
    
    return scores_dict, details

if __name__ == "__main__":
    evaluate_rag_retriever(verbose=True, test_mode=False) 