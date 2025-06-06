"""
Evaluation script for RAG components.
Runs evaluations for the query analyzer, response generator, and retriever components.
"""

from .rag_query_analyzer.evaluate_rag_query_analyzer import evaluate_query_analyzer
from .rag_response_generator.evaluate_rag_response_generator import evaluate_response_generator
from .rag_retriever.evaluate_rag_retriever import evaluate_rag_retriever
from .router.evaluate_router import evaluate_router
import json
import os
from datetime import datetime
from typing import Dict, Any, List
import time

def print_section_header(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 50)
    print(title.center(50))
    print("=" * 50 + "\n")

def save_results(results: dict, detailed_results: Dict[str, List[Dict[str, Any]]]) -> None:
    """
    Save evaluation results to JSON and text files.
    
    Args:
        results: Dictionary containing component scores
        detailed_results: Dictionary containing detailed test results for each component
    """
    # Create results directory if it doesn't exist
    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Add timestamp to results
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results["timestamp"] = timestamp
    
    # Save JSON results
    json_filename = f"eval_results_{timestamp}.json"
    json_filepath = os.path.join(results_dir, json_filename)
    with open(json_filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    # Also save as latest.json
    latest_filepath = os.path.join(results_dir, "latest.json")
    with open(latest_filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    # Save detailed report
    report_filename = f"eval_report_{timestamp}.txt"
    report_filepath = os.path.join(results_dir, report_filename)
    save_detailed_report(results, detailed_results, report_filepath)
    
    # Also save as latest_report.txt
    latest_report_filepath = os.path.join(results_dir, "latest_report.txt")
    save_detailed_report(results, detailed_results, latest_report_filepath)
    
    print(f"\nResults saved to:")
    print(f"- {json_filepath}")
    print(f"- {report_filepath}")
    print(f"- {latest_filepath}")
    print(f"- {latest_report_filepath}")

def save_detailed_report(
    results: dict,
    detailed_results: Dict[str, List[Dict[str, Any]]],
    filepath: str
) -> None:
    """
    Save a detailed evaluation report to a text file.
    
    Args:
        results: Dictionary containing component scores
        detailed_results: Dictionary containing detailed test results for each component
        filepath: Path to save the report to
    """
    with open(filepath, "w", encoding="utf-8") as f:
        # Write header
        f.write("RAG Components Evaluation Report\n")
        f.write("=============================\n\n")
        f.write(f"Generated on: {results['timestamp']}\n\n")
        
        # Write overall scores
        f.write("Overall Scores\n")
        f.write("-------------\n")
        f.write(f"Total Score: {results['Overall']:.2f}\n")
        f.write(f"Query Analyzer Score: {results['Query Analyzer']['Overall']:.2f}\n")
        f.write(f"Response Generator Score: {results['Response Generator']['Overall']:.2f}\n")
        f.write(f"Retriever Score: {results['Retriever']['Overall']:.2f}\n")
        f.write(f"Router Score: {results['Router']['Routing Accuracy']:.2f}\n\n")
        
        # Write Query Analyzer results
        f.write("Query Analyzer Results\n")
        f.write("---------------------\n")
        for metric, score in results["Query Analyzer"].items():
            if metric != "Overall":
                f.write(f"{metric}: {score:.2f}\n")
        
        f.write("\nDetailed Test Results:\n")
        for test in detailed_results["Query Analyzer"]:
            f.write(f"\nMetric: {test['metric']}\n")
            f.write(f"Query: {test['query']}\n")
            if "chat_history" in test:
                f.write(f"Chat History:\n{test['chat_history']}\n")
            f.write(f"Generated: {test['generated']}\n")
            f.write(f"Score: {test['score']:.2f}\n")
            if "reasoning_steps" in test:
                f.write("Reasoning steps:\n")
                for step in test["reasoning_steps"]:
                    f.write(f"- {step}\n")
            f.write("-" * 50 + "\n")
        
        # Write Response Generator results
        f.write("\nResponse Generator Results\n")
        f.write("-------------------------\n")
        for metric, score in results["Response Generator"].items():
            if metric != "Overall":
                f.write(f"{metric}: {score:.2f}\n")
        
        f.write("\nDetailed Test Results:\n")
        for test in detailed_results["Response Generator"]:
            f.write(f"\nMetric: {test['metric']}\n")
            f.write(f"Query: {test['query']}\n")
            if "context" in test:
                f.write(f"Context: {test['context']}\n")
            f.write(f"Generated: {test['generated']}\n")
            if "expected" in test:
                f.write(f"Expected: {test['expected']}\n")
            f.write(f"Score: {test['score']:.2f}\n")
            if "reasoning_steps" in test:
                f.write("Reasoning steps:\n")
                for step in test["reasoning_steps"]:
                    f.write(f"- {step}\n")
            f.write("-" * 50 + "\n")
            
        # Write Retriever results
        f.write("\nRetriever Results\n")
        f.write("-----------------\n")
        for metric, score in results["Retriever"].items():
            if metric != "Overall":
                f.write(f"{metric}: {score:.2f}\n")
        
        f.write("\nDetailed Test Results:\n")
        for test in detailed_results["Retriever"]:
            # Count contexts with relevant information (contexts covering ground truth statements)
            contexts_with_relevant_info = sum(
                1 for ctx in test['recall_details']['per_context_results'] 
                if ctx['coverage_counts'].get('full', 0) > 0 or ctx['coverage_counts'].get('partial', 0) > 0
            )

            f.write(f"\nQuery: {test['query']}\n")
            f.write(f"Retrieved contexts: {test['retrieved_contexts']}\n")
            f.write(f"Ground truth: {test['ground_truth']}\n")
            f.write(f"Relevancy score (best): {test['relevancy_details']['relevancy_ratio_best']:.2f}\n")
            f.write(f"Relevancy score (all): {test['relevancy_details']['relevancy_ratio_all']:.2f}\n")
            f.write(f"Recall score: {test['recall_details']['recall_score']:.2f}\n")
            f.write(f"Weighted recall score: {test['recall_details']['weighted_recall_score']:.2f}\n")            
            f.write(f"Total ground truth statements to cover: {test['recall_details']['total_statements']}\n")
            f.write(f"Contexts covering ground truth statements: {contexts_with_relevant_info}/{test['total_contexts']}\n")
            f.write(f"Overall score: {test['score']:.2f}\n")

            f.write("\nPer-context relevancy evaluation:\n")
            for ctx_result in test['relevancy_details']['per_context_results']:
                f.write(f"\nContext {ctx_result['context_num']}:\n")
                f.write(f"Content: {ctx_result['context']}\n")
                f.write(f"Is relevant: {ctx_result['is_relevant']}\n")
                f.write("Reasoning:\n")
                for step in ctx_result['reasoning_steps']:
                    f.write(f"- {step}\n")
            f.write("\nPer-context recall evaluation:\n")
            for ctx_result in test['recall_details']['per_context_results']:
                f.write(f"\nContext {ctx_result['context_num']}:\n")
                f.write(f"Content: {ctx_result['context']}\n")
                
                # Modified to use the coverage information from our structure
                coverage_full = ctx_result['coverage_counts'].get('full', 0)
                coverage_partial = ctx_result['coverage_counts'].get('partial', 0)
                has_relevant = coverage_full > 0 or coverage_partial > 0
                
                f.write(f"Has relevant information: {has_relevant}\n")
                f.write("Coverage details:\n")
                f.write(f"- Full coverage: {coverage_full}\n")
                f.write(f"- Partial coverage: {coverage_partial}\n")
                f.write(f"- No coverage: {ctx_result['coverage_counts'].get('none', 0)}\n")
                
                # Add coverage assessment details
                f.write("Statement coverage assessment:\n")
                for assessment in ctx_result.get('coverage_assessments', []):
                    f.write(f"- Statement: \"{assessment.get('statement', '')}\" - Coverage: {assessment.get('coverage', 'none').upper()}\n")
                    f.write(f"  Reasoning: {assessment.get('reasoning', 'No reasoning provided')}\n")

            f.write("-" * 50 + "\n")

        # Write Router results
        f.write("\nRouter Results\n")
        f.write("-----------------\n")
        for metric, score in results["Router"].items():
            if metric != "Overall":
                f.write(f"{metric}: {score:.2f}\n")
        
        f.write("\nDetailed Test Results:\n")
        for test in detailed_results["Router"]:
            f.write(f"\nMetric: {test['metric']}\n")
            f.write(f"Query: {test['query']}\n")
            f.write(f"Chat History:\n{test['chat_history']}\n")
            f.write(f"Decision Path: {test['decision_path']}\n")
            f.write(f"Expected Paths: {test['expected_paths']}\n")
            f.write(f"Reasoning Steps: {test['reasoning_steps']}\n")
            f.write(f"Score: {test['score']:.2f}\n")
            f.write("-" * 50 + "\n")

def main() -> None:
    """Run evaluations for all RAG components."""
    start_time = time.time()
    
    print_section_header("Evaluating RAG Components")
    
    # Evaluate Query Analyzer
    print("Evaluating Query Analyzer...")
    qa_scores, qa_details = evaluate_query_analyzer(verbose=False)
    
    # Evaluate Response Generator
    print("\nEvaluating Response Generator...")
    rg_scores, rg_details = evaluate_response_generator(verbose=False)
    
    # Evaluate Retriever
    print("\nEvaluating Retriever...")
    rt_scores, rt_details = evaluate_rag_retriever(verbose=False)

    # Evaluate Router
    print("\nEvaluating Router...")
    router_scores, router_details = evaluate_router(verbose=False)
    
    # Calculate overall score
    overall_score = (qa_scores["Overall"] + rg_scores["Overall"] + rt_scores["Overall"] + router_scores['Routing Accuracy']) / 4
    
    # Calculate total time
    total_time = time.time() - start_time
    
    # Prepare results
    results = {
        "Overall": overall_score,
        "Query Analyzer": qa_scores,
        "Response Generator": rg_scores,
        "Retriever": rt_scores,
        "Router": router_scores,
        "Total Time (seconds)": total_time
    }
    
    detailed_results = {
        "Query Analyzer": qa_details,
        "Response Generator": rg_details,
        "Retriever": rt_details,
        "Router": router_details
    }
    
    # Print overall results
    print_section_header("Final Results")
    print(f"Query Analyzer Score: {qa_scores['Overall']:.2f}")
    print(f"Response Generator Score: {rg_scores['Overall']:.2f}")
    print(f"Retriever Score: {rt_scores['Overall']:.2f}")
    print(f"Router Score: {router_scores['Routing Accuracy']:.2f}")
    print(f"Overall Score: {overall_score:.2f}")
    print(f"Total Time: {total_time:.2f} seconds")
    
    # Save results
    save_results(results, detailed_results)

if __name__ == "__main__":
    main() 
