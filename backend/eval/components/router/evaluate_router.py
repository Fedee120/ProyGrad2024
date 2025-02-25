from .metrics.routing_accuracy import evaluate_routing_accuracy
from agent.router import Router
import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Tuple
from eval.helpers.eval_helper import create_chat_history, format_chat_history_from_dict
from collections import defaultdict

def calculate_weighted_routing_accuracy(dataset, details):
    # Count the number of samples of each path in the dataset
    path_counts = defaultdict(int)
    for sample in dataset:
        for path in sample["expected_paths"]:
            path_counts[path] += 1

    # Count correct classifications per path
    correct_classifications = defaultdict(int)
    for detail in details:
        decision_path = detail["decision_path"]
        expected_paths = detail["expected_paths"]
        
        if decision_path in expected_paths:  # Router made a correct choice
            for path in expected_paths:
                # Credit all expected paths when the router makes a correct choice.  
                # This prevents other valid expected paths from being incorrectly counted as misclassified.
                correct_classifications[path] += 1

    # Compute weighted routing accuracy
    weighted_accuracy = 0
    total_samples = sum(len(sample["expected_paths"]) for sample in dataset) 
    # Count total expected path instances, not just test cases.  
    # Samples with multiple valid paths are counted once per path to ensure their contribution is properly reflected in the accuracy calculation.

    for path, count in path_counts.items():
        path_accuracy = correct_classifications[path] / count if count > 0 else 0
        weight = count / total_samples  # Weight based on dataset distribution
        weighted_accuracy += path_accuracy * weight

    return weighted_accuracy

def evaluate_routing_accuracy_samples(
    router: Router,
    samples: List[Dict[str, Any]],
    verbose: bool = False
) -> Tuple[List[float], List[Dict[str, Any]]]:
    """
    Evaluate whether the router correctly classifies multiple samples.
    """
    
    def evaluate_single_sample(sample: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate whether the router correctly classifies a single sample.
        """

        # Convert chat history data to message objects
        chat_history = create_chat_history(sample["chat_history"])

        # Obtain router decision path
        decision_path, reasoning_steps = router.get_decision_path(sample["query"], chat_history)
        
        # Evaluate whether the router correctly classifies the query into the correct decision path
        score = evaluate_routing_accuracy(
            query=sample["query"],
            chat_history=chat_history,
            decision_path=decision_path,
            expected_paths=sample["expected_paths"],
            reasoning_steps=reasoning_steps,
            verbose=verbose
        )
        
        # Store test details
        test_details = {
            "metric": "Routing Accuracy",
            "query": sample["query"],
            "chat_history": format_chat_history_from_dict(sample["chat_history"]),
            "decision_path": decision_path,
            "expected_paths": sample["expected_paths"],
            "reasoning_steps": reasoning_steps,
            "score": score
        }
            
        return score, test_details
    
    scores = []
    details = []

    # Process samples in parallel
    with ThreadPoolExecutor(max_workers=len(samples)) as executor:
        futures = [executor.submit(evaluate_single_sample, sample) for sample in samples]

    for future in futures:
        score, test_details = future.result()
        scores.append(score)
        details.append(test_details)
            
    return scores, details

def evaluate_router(verbose: bool = False) -> Tuple[Dict[str, float], List[Dict[str, Any]]]:
    """
    Run all evaluations for the Router.
    
    Args:
        verbose: Whether to print detailed evaluation information
        
    Returns:
        Tuple[Dict[str, float], List[Dict[str, Any]]]: Dictionary mapping metric name to their score, and list of detailed test results for each sample.
    """
    
    router = Router()
    
    # Load test dataset
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(current_dir, "datasets", "router_dataset.json")
    
    with open(dataset_path, encoding="utf-8") as f:
        dataset = json.load(f)
    
    scores = {}
    
    # Evaluate the router's classification performance on all test samples
    ra_scores, ra_details = evaluate_routing_accuracy_samples(router, dataset, verbose)
    
    # Calculate weighted routing accuracy
    routing_accuracy = calculate_weighted_routing_accuracy(dataset, ra_details)
    if verbose:
        print(f"Routing Accuracy: {routing_accuracy:.2f} ({len(ra_scores)} samples)")    

    scores["Routing Accuracy"] = routing_accuracy

    return scores, ra_details

if __name__ == "__main__":
    evaluate_router(verbose=True) 