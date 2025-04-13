# Routing Accuracy: Measures the percentage of correctly classified queries.
# Routing Accuracy = Number of correctly routed queries / Total queries tested

from typing import List, Tuple
from agent.router import Router
from langchain_core.messages import AIMessage, HumanMessage
from eval.helpers.eval_helper import format_chat_history_from_messages, create_chat_history
import json
import os

def evaluate_routing_accuracy(
    query: str,
    chat_history: List[AIMessage | HumanMessage],
    decision_path: str,
    expected_paths: List[str],
    reasoning_steps: str,
    verbose: bool = False
) -> Tuple[float, List[str]]:
    """
    Evaluate whether the router correctly classifies a query into the correct decision path.

    Args:
        query (str): The user’s query.
        chat_history: List[AIMessage | HumanMessage]: The conversation history.
        decision_path (str): The decision path selected by the router.
        expected_paths (List[str]): The correct decision paths for this query.
        verbose (bool): Whether to print detailed evaluation information.

    Returns:
        float: 1.0 if the decision path to take is correctly choosen, 0.0 if not
    """

    is_path_correct = decision_path in expected_paths

    if verbose:
        print("\nEvaluating routing accuracy:")
        print(f"\nQuery: {query}")
        print("\nChat History:")
        print(format_chat_history_from_messages(chat_history))
        print(f"\nDecision path selected by the router: {decision_path}")
        print(f"\nExpected decision paths: {expected_paths}")
        print(f"\nReasoning Steps:\n{reasoning_steps}")
        print(f"\nDecision path to take is correctly choosen?: {is_path_correct}\n")

    return float(is_path_correct)

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(current_dir, "..", "datasets", "router_dataset.json")
    with open(dataset_path, encoding="utf-8") as f:
        dataset = json.load(f)
    
    sample = dataset[0]

    chat_history = create_chat_history(sample["chat_history"])

    router = Router()
    decision_path, reasoning_steps = router.get_decision_path(sample["query"], chat_history)

    print(evaluate_routing_accuracy(sample["query"], chat_history, decision_path, sample["expected_paths"],reasoning_steps, verbose=True)) 