"""
Evaluation script for RAG components.
Runs evaluations for the query analyzer, response generator, and retriever components.
"""

from .rag_query_analyzer.evaluate_rag_query_analyzer import evaluate_query_analyzer
from .rag_response_generator.evaluate_rag_response_generator import evaluate_response_generator
from .rag_retriever.evaluate_rag_retriever import evaluate_rag_retriever
from dotenv import load_dotenv
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
        f.write(f"Retriever Score: {results['Retriever']['Overall']:.2f}\n\n")
        
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
            f.write(f"\nQuery: {test['query']}\n")
            f.write(f"Retrieved contexts: {test['retrieved_contexts']}\n")
            f.write(f"Ground truth: {test['ground_truth']}\n")
            f.write(f"Relevancy score (best): {test['relevancy_details']['relevancy_ratio_best']:.2f}\n")
            f.write(f"Relevancy score (all): {test['relevancy_details']['relevancy_ratio_all']:.2f}\n")
            f.write("\nPer-context relevancy evaluation:\n")
            for ctx_result in test['relevancy_details']['per_context_results']:
                f.write(f"\nContext {ctx_result['context_num']}:\n")
                f.write(f"Content: {ctx_result['context']}\n")
                f.write(f"Is relevant: {ctx_result['is_relevant']}\n")
                f.write("Reasoning:\n")
                for step in ctx_result['reasoning_steps']:
                    f.write(f"- {step}\n")
            f.write(f"Recall score (best): {test['recall_details']['recall_score_best']:.2f}\n")
            f.write(f"Recall score (all): {test['recall_details']['recall_score_all']:.2f}\n")
            f.write("\nPer-context recall evaluation:\n")
            for ctx_result in test['recall_details']['per_context_results']:
                f.write(f"\nContext {ctx_result['context_num']}:\n")
                f.write(f"Content: {ctx_result['context']}\n")
                f.write(f"Has relevant information: {ctx_result['has_relevant_information']}\n")
                f.write("Reasoning:\n")
                for step in ctx_result['reasoning_steps']:
                    f.write(f"- {step}\n")
            f.write(f"\nTotal relevant contexts: {test['recall_details']['relevant_contexts']}/{test['recall_details']['total_contexts']}\n")
            f.write(f"Overall score: {test['score']:.2f}\n")
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
    
    # Calculate overall score
    overall_score = (qa_scores["Overall"] + rg_scores["Overall"] + rt_scores["Overall"]) / 3
    
    # Calculate total time
    total_time = time.time() - start_time
    
    # Prepare results
    results = {
        "Overall": overall_score,
        "Query Analyzer": qa_scores,
        "Response Generator": rg_scores,
        "Retriever": rt_scores,
        "Total Time (seconds)": total_time
    }
    
    detailed_results = {
        "Query Analyzer": qa_details,
        "Response Generator": rg_details,
        "Retriever": rt_details
    }
    
    # Print overall results
    print_section_header("Final Results")
    print(f"Query Analyzer Score: {qa_scores['Overall']:.2f}")
    print(f"Response Generator Score: {rg_scores['Overall']:.2f}")
    print(f"Retriever Score: {rt_scores['Overall']:.2f}")
    print(f"Overall Score: {overall_score:.2f}")
    print(f"Total Time: {total_time:.2f} seconds")
    
    # Save results
    save_results(results, detailed_results)

if __name__ == "__main__":
    main() 