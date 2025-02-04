from .metrics.splits_when_needed import evaluate_splits_when_needed
from .metrics.resolves_references import evaluate_resolves_references
from .metrics.replaces_acronyms import evaluate_replaces_acronyms
from agent.llms.rag_query_analyzer import RAGQueryAnalyzer
from tqdm import tqdm
import json
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
from langchain_core.messages import AIMessage, HumanMessage

def _create_chat_history(history_data: List[Dict[str, str]]) -> List[AIMessage | HumanMessage]:
    """Convert chat history data to message objects."""
    messages = []
    for msg in history_data:
        if msg["role"] == "human":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    return messages

def evaluate_expansion_samples(
    analyzer: RAGQueryAnalyzer,
    samples: List[Dict[str, Any]],
    verbose: bool = False
) -> List[float]:
    """Evaluate expansion test samples."""
    scores = []
    for sample in samples:
        result = analyzer.analyze(sample["original_query"], [])
        score = evaluate_splits_when_needed(
            original_query=sample["original_query"],
            generated_queries=result.queries,
            expected_queries=sample["expected_queries"],
            verbose=verbose
        )
        scores.append(score)
    return scores

def evaluate_references_samples(
    analyzer: RAGQueryAnalyzer,
    samples: List[Dict[str, Any]],
    verbose: bool = False
) -> List[float]:
    """Evaluate reference resolution test samples."""
    scores = []
    for sample in samples:
        # Convert chat history to message objects
        chat_history = _create_chat_history(sample["chat_history"])
        
        # Get analyzer's output with chat history
        result = analyzer.analyze(sample["original_query"], chat_history)
        
        score = evaluate_resolves_references(
            original_query=sample["original_query"],
            generated_query=result.updated_query,
            expected_query=sample["expected_query"],
            chat_history=chat_history,
            verbose=verbose
        )
        scores.append(score)
    return scores

def evaluate_acronyms_samples(
    analyzer: RAGQueryAnalyzer,
    samples: List[Dict[str, Any]],
    verbose: bool = False
) -> List[float]:
    """Evaluate acronym replacement test samples."""
    scores = []
    for sample in samples:
        result = analyzer.analyze(sample["original_query"], [])
        score = evaluate_replaces_acronyms(
            original_query=sample["original_query"],
            generated_query=result.updated_query,
            expected_query=sample["expected_query"],
            verbose=verbose
        )
        scores.append(score)
    return scores

if __name__ == "__main__":
    load_dotenv()
    
    analyzer = RAGQueryAnalyzer()
    
    # Load test dataset
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(current_dir, "datasets", "query_analyzer_dataset.json")
    
    with open(dataset_path, encoding="utf-8") as f:
        dataset = json.load(f)
    
    # Process each test set in parallel
    with ThreadPoolExecutor() as executor:
        futures = []
        
        if "expansion_tests" in dataset:
            futures.append(
                executor.submit(
                    evaluate_expansion_samples,
                    analyzer,
                    dataset["expansion_tests"],
                    True
                )
            )
        
        if "references_tests" in dataset:
            futures.append(
                executor.submit(
                    evaluate_references_samples,
                    analyzer,
                    dataset["references_tests"],
                    True
                )
            )
        
        if "acronyms_tests" in dataset:
            futures.append(
                executor.submit(
                    evaluate_acronyms_samples,
                    analyzer,
                    dataset["acronyms_tests"],
                    True
                )
            )
        
        # Get results
        results = [future.result() for future in futures]
    
    # Calculate scores for each metric
    if "expansion_tests" in dataset:
        expansion_scores = results.pop(0)
        expansion_avg = sum(expansion_scores) / len(expansion_scores)
        print(f"\nExpands When Needed: {expansion_avg:.2f} ({len(expansion_scores)} samples)")
    
    if "references_tests" in dataset:
        references_scores = results.pop(0)
        references_avg = sum(references_scores) / len(references_scores)
        print(f"Resolves References: {references_avg:.2f} ({len(references_scores)} samples)")
    
    if "acronyms_tests" in dataset:
        acronyms_scores = results.pop(0)
        acronyms_avg = sum(acronyms_scores) / len(acronyms_scores)
        print(f"Replaces Acronyms: {acronyms_avg:.2f} ({len(acronyms_scores)} samples)")
    
    # Calculate overall score
    all_scores = []
    if "expansion_tests" in dataset:
        all_scores.extend(expansion_scores)
    if "references_tests" in dataset:
        all_scores.extend(references_scores)
    if "acronyms_tests" in dataset:
        all_scores.extend(acronyms_scores)
    
    overall_score = sum(all_scores) / len(all_scores)
    print(f"\nOverall Score: {overall_score:.2f} ({len(all_scores)} total samples)") 