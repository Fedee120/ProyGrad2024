from .metrics.resolves_references import evaluate_resolves_references
from .metrics.expands_acronyms import evaluate_expands_acronyms
from .metrics.includes_context import evaluate_includes_context
from agent.llms.rag_query_analyzer import RAGQueryAnalyzer
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
    """
    Evaluate if generated queries expand acronyms when present.
    Tests if the model expands acronyms in at least one query.
    """
    scores = []
    for sample in samples:
        # Generate queries
        generated_queries = analyzer.analyze(sample["original_query"], [])
        
        # Check if acronyms are expanded
        score = evaluate_expands_acronyms(
            original_query=sample["original_query"],
            queries=generated_queries.queries,
            verbose=verbose
        )
        
        if verbose:
            print(f"\nEvaluating acronym expansion for: {sample['original_query']}")
            print(f"Generated queries: {generated_queries.queries}")
            print(f"Expected queries: {sample['expected_queries']}")
            print(f"Score: {score:.2f}")
        scores.append(score)
    return scores

def evaluate_context_samples(
    analyzer: RAGQueryAnalyzer,
    samples: List[Dict[str, Any]],
    verbose: bool = False
) -> List[float]:
    """
    Evaluate if generated queries consider conversation context.
    Tests if the model incorporates context from previous messages.
    """
    scores = []
    for sample in samples:
        # Convert chat history to message objects
        chat_history = _create_chat_history(sample["chat_history"])
        
        # Get analyzer's output with chat history
        result = analyzer.analyze(sample["original_query"], chat_history)
        
        # Check if context is included
        score = evaluate_includes_context(
            original_query=sample["original_query"],
            queries=result.queries,
            updated_query=result.updated_query,
            chat_history=chat_history,
            verbose=verbose
        )
        
        if verbose:
            print(f"\nEvaluating context inclusion for: {sample['original_query']}")
            print(f"Chat history: {chat_history}")
            print(f"Generated queries: {result.queries}")
            print(f"Updated query: {result.updated_query}")
            print(f"Score: {score:.2f}")
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
        
        if "resolves_references_tests" in dataset:
            futures.append(
                executor.submit(
                    evaluate_references_samples,
                    analyzer,
                    dataset["resolves_references_tests"],
                    True
                )
            )
        
        if "expands_acronyms_tests" in dataset:
            futures.append(
                executor.submit(
                    evaluate_acronyms_samples,
                    analyzer,
                    dataset["expands_acronyms_tests"],
                    True
                )
            )
            
        if "includes_context_tests" in dataset:
            futures.append(
                executor.submit(
                    evaluate_context_samples,
                    analyzer,
                    dataset["includes_context_tests"],
                    True
                )
            )
        
        # Get results
        results = [future.result() for future in futures]
    
    # Calculate scores for each metric
    if "resolves_references_tests" in dataset:
        references_scores = results.pop(0)
        references_avg = sum(references_scores) / len(references_scores)
        print(f"\nReference Resolution: {references_avg:.2f} ({len(references_scores)} samples)")
    
    if "expands_acronyms_tests" in dataset:
        acronyms_scores = results.pop(0)
        acronyms_avg = sum(acronyms_scores) / len(acronyms_scores)
        print(f"Acronym Expansion: {acronyms_avg:.2f} ({len(acronyms_scores)} samples)")
        
    if "includes_context_tests" in dataset:
        context_scores = results.pop(0)
        context_avg = sum(context_scores) / len(context_scores)
        print(f"Context Inclusion: {context_avg:.2f} ({len(context_scores)} samples)")
    
    # Calculate overall score
    all_scores = []
    if "resolves_references_tests" in dataset:
        all_scores.extend(references_scores)
    if "expands_acronyms_tests" in dataset:
        all_scores.extend(acronyms_scores)
    if "includes_context_tests" in dataset:
        all_scores.extend(context_scores)
    
    overall_score = sum(all_scores) / len(all_scores)
    print(f"\nOverall Score: {overall_score:.2f} ({len(all_scores)} total samples)") 