from .metrics.answer_correctness import evaluate_answer_correctness
from .metrics.answer_relevancy import evaluate_answer_relevancy
from .metrics.faithfulness import evaluate_faithfulness
from .metrics.acknowledge_contradiction import evaluate_acknowledge_contradiction
from .metrics.citations_real_and_used import evaluate_citations_real_and_used
from agent.llms.rag_response_generator import RAGResponseGenerator
from agent.rag import SearchResult
import json
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Tuple
from langchain.schema import Document

def evaluate_faithfulness_samples(
    generator: RAGResponseGenerator,
    samples: List[Dict[str, Any]],
    verbose: bool = False
) -> Tuple[List[float], List[Dict[str, Any]]]:
    """Evaluate faithfulness test samples."""
    scores = []
    details = []
    
    def evaluate_single_sample(sample: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        # Generate answer using the provided context
        generated_answer = generator.generate_response(
            question=sample["question"],
            search_results=sample["context"]
        )
        
        # Evaluate if the answer only uses information from the context
        score, reasoning_steps = evaluate_faithfulness(
            question=sample["question"],
            facts=sample["context"],
            answer=generated_answer.answer,
            verbose=verbose
        )
        
        # Store test details
        test_details = {
            "metric": "Faithfulness",
            "query": sample["question"],
            "context": sample["context"],
            "generated": generated_answer.answer,
            "score": score,
            "reasoning_steps": reasoning_steps
        }
        
        if verbose:
            print(f"\nEvaluating faithfulness for: {sample['question']}")
            print(f"Context provided: {sample['context']}")
            print(f"Generated answer: {generated_answer.answer}")
            print(f"Score: {score:.2f}")
            
        return score, test_details
    
    # Process samples in parallel
    with ThreadPoolExecutor(max_workers=len(samples)) as executor:
        futures = [executor.submit(evaluate_single_sample, sample) for sample in samples]
        for future in futures:
            score, test_details = future.result()
            scores.append(score)
            details.append(test_details)
            
    return scores, details

def evaluate_correctness_samples(
    generator: RAGResponseGenerator,
    samples: List[Dict[str, Any]],
    verbose: bool = False
) -> Tuple[List[float], List[Dict[str, Any]]]:
    """Evaluate answer correctness test samples."""
    scores = []
    details = []
    
    def evaluate_single_sample(sample: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        # Generate answer with context
        generated_answer = generator.generate_response(
            question=sample["question"],
            search_results=sample["context"]
        )
        
        # Compare generated answer with expected answer
        score, reasoning_steps = evaluate_answer_correctness(
            question=sample["question"],
            answer=generated_answer.answer,
            ground_truth=sample["expected_answer"],
            verbose=verbose
        )
        
        # Store test details
        test_details = {
            "metric": "Answer Correctness",
            "query": sample["question"],
            "context": sample["context"],
            "generated": generated_answer.answer,
            "expected": sample["expected_answer"],
            "score": score,
            "reasoning_steps": reasoning_steps
        }
        
        if verbose:
            print(f"\nEvaluating correctness for: {sample['question']}")
            print(f"Context provided: {sample['context']}")
            print(f"Generated answer: {generated_answer.answer}")
            print(f"Expected answer: {sample['expected_answer']}")
            print(f"Score: {score:.2f}")
            
        return score, test_details
    
    # Process samples in parallel
    with ThreadPoolExecutor(max_workers=len(samples)) as executor:
        futures = [executor.submit(evaluate_single_sample, sample) for sample in samples]
        for future in futures:
            score, test_details = future.result()
            scores.append(score)
            details.append(test_details)
            
    return scores, details

def evaluate_relevancy_samples(
    generator: RAGResponseGenerator,
    samples: List[Dict[str, Any]],
    verbose: bool = False
) -> Tuple[List[float], List[Dict[str, Any]]]:
    """Evaluate answer relevancy test samples."""
    scores = []
    details = []
    
    def evaluate_single_sample(sample: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        # Generate answer with context
        generated_answer = generator.generate_response(
            question=sample["question"],
            search_results=sample["context"]
        )
        
        # Check if answer is relevant to the question within the given context
        score, reasoning_steps = evaluate_answer_relevancy(
            question=sample["question"],
            answer=generated_answer.answer,
            verbose=verbose
        )
        
        # Store test details
        test_details = {
            "metric": "Answer Relevancy",
            "query": sample["question"],
            "context": sample["context"],
            "generated": generated_answer.answer,
            "score": score,
            "reasoning_steps": reasoning_steps
        }
        
        if verbose:
            print(f"\nEvaluating relevancy for: {sample['question']}")
            print(f"Context provided: {sample['context']}")
            print(f"Generated answer: {generated_answer.answer}")
            print(f"Score: {score:.2f}")
            
        return score, test_details
    
    # Process samples in parallel
    with ThreadPoolExecutor(max_workers=len(samples)) as executor:
        futures = [executor.submit(evaluate_single_sample, sample) for sample in samples]
        for future in futures:
            score, test_details = future.result()
            scores.append(score)
            details.append(test_details)
            
    return scores, details

def evaluate_contradictions_samples(
    generator: RAGResponseGenerator,
    samples: List[Dict[str, Any]],
    verbose: bool = False
) -> Tuple[List[float], List[Dict[str, Any]]]:
    """Evaluate contradiction acknowledgment test samples."""
    scores = []
    details = []
    
    def evaluate_single_sample(sample: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        # Generate answer with context
        generated_answer = generator.generate_response(
            question=sample["question"],
            search_results=sample["context"]
        )
        
        # Check if answer acknowledges contradictions when present
        score, reasoning_steps = evaluate_acknowledge_contradiction(
            question=sample["question"],
            answer=generated_answer.answer,
            context=sample["context"],
            verbose=verbose
        )
        
        # Store test details
        test_details = {
            "metric": "Contradiction Acknowledgment",
            "query": sample["question"],
            "context": sample["context"],
            "generated": {
                "answer": generated_answer.answer,
                "citations": generated_answer.context
            },
            "score": score,
            "reasoning_steps": reasoning_steps
        }
        
        if verbose:
            print(f"\nEvaluating contradiction acknowledgment for: {sample['question']}")
            print(f"Context provided: {sample['context']}")
            print(f"Generated answer: {generated_answer.answer}")
            print(f"Citations: {generated_answer.context}")
            print(f"Score: {score:.2f}")
            
        return score, test_details
    
    # Process samples in parallel
    with ThreadPoolExecutor(max_workers=len(samples)) as executor:
        futures = [executor.submit(evaluate_single_sample, sample) for sample in samples]
        for future in futures:
            score, test_details = future.result()
            scores.append(score)
            details.append(test_details)
            
    return scores, details

def evaluate_citations_samples(
    generator: RAGResponseGenerator,
    samples: List[Dict[str, Any]],
    verbose: bool = False
) -> Tuple[List[float], List[Dict[str, Any]]]:
    """Evaluate citations test samples."""
    scores = []
    details = []
    
    def evaluate_single_sample(sample: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        # Convert context to SearchResult objects
        search_results = []
        for result in sample["context"]:
            documents = [
                Document(
                    page_content=doc["page_content"],
                    metadata=doc["metadata"]
                ) for doc in result["documents"]
            ]
            search_results.append(
                SearchResult(
                    query=result["query"],
                    documents=documents
                )
            )
        formatted_context = []
        for result in search_results:
            formatted_context.extend(result.formatted())
        context_str = "\n\n".join(formatted_context)
    
        # Generate answer with context
        generated_answer = generator.generate_response(
            question=sample["question"],
            search_results=context_str
        )
        
        # Check if citations are real and properly used
        score, reasoning_steps = evaluate_citations_real_and_used(
            question=sample["question"],
            answer=generated_answer.answer,
            citations=generated_answer.context,
            context=context_str,
            verbose=verbose
        )
        
        # Store test details
        test_details = {
            "metric": "Citations Real and Used",
            "query": sample["question"],
            "context": context_str,
            "generated": {
                "answer": generated_answer.answer,
                "citations": generated_answer.context
            },
            "score": score,
            "reasoning_steps": reasoning_steps
        }
        
        if verbose:
            print(f"\nEvaluating citations for: {sample['question']}")
            print(f"Context provided: {context_str}")
            print(f"Generated answer: {generated_answer.answer}")
            print(f"Citations: {generated_answer.context}")
            print(f"Score: {score:.2f}")
            
        return score, test_details
    
    # Process samples in parallel
    with ThreadPoolExecutor(max_workers=len(samples)) as executor:
        futures = [executor.submit(evaluate_single_sample, sample) for sample in samples]
        for future in futures:
            score, test_details = future.result()
            scores.append(score)
            details.append(test_details)
            
    return scores, details

def evaluate_response_generator(verbose: bool = False) -> Tuple[Dict[str, float], List[Dict[str, Any]]]:
    """
    Run all evaluations for the RAG Response Generator component.
    
    Args:
        verbose: Whether to print detailed evaluation information
        
    Returns:
        Tuple[Dict[str, float], List[Dict[str, Any]]]: Dictionary mapping metric names to their scores,
        and list of detailed test results
    """
    load_dotenv()
    
    generator = RAGResponseGenerator()
    
    # Load test dataset
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(current_dir, "datasets", "response_generator_dataset.json")
    
    with open(dataset_path, encoding="utf-8") as f:
        dataset = json.load(f)
    
    scores = {}
    all_details = []
    
    # Process each test set in parallel
    with ThreadPoolExecutor() as executor:
        futures = []
        
        if "faithfulness_tests" in dataset:
            futures.append(
                executor.submit(
                    evaluate_faithfulness_samples,
                    generator,
                    dataset["faithfulness_tests"],
                    verbose
                )
            )
        
        if "answer_correctness_tests" in dataset:
            futures.append(
                executor.submit(
                    evaluate_correctness_samples,
                    generator,
                    dataset["answer_correctness_tests"],
                    verbose
                )
            )
            
        if "answer_relevancy_tests" in dataset:
            futures.append(
                executor.submit(
                    evaluate_relevancy_samples,
                    generator,
                    dataset["answer_relevancy_tests"],
                    verbose
                )
            )
            
        if "acknowledge_contradiction_tests" in dataset:
            futures.append(
                executor.submit(
                    evaluate_contradictions_samples,
                    generator,
                    dataset["acknowledge_contradiction_tests"],
                    verbose
                )
            )
            
        if "citations_real_and_used_tests" in dataset:
            futures.append(
                executor.submit(
                    evaluate_citations_samples,
                    generator,
                    dataset["citations_real_and_used_tests"],
                    verbose
                )
            )
        
        # Get results
        results = [future.result() for future in futures]
    
    # Calculate scores for each metric
    if "faithfulness_tests" in dataset:
        faithfulness_scores, faithfulness_details = results.pop(0)
        faithfulness_avg = sum(faithfulness_scores) / len(faithfulness_scores)
        scores["Faithfulness"] = faithfulness_avg
        all_details.extend(faithfulness_details)
        if verbose:
            print(f"\nFaithfulness: {faithfulness_avg:.2f} ({len(faithfulness_scores)} samples)")
    
    if "answer_correctness_tests" in dataset:
        correctness_scores, correctness_details = results.pop(0)
        correctness_avg = sum(correctness_scores) / len(correctness_scores)
        scores["Answer Correctness"] = correctness_avg
        all_details.extend(correctness_details)
        if verbose:
            print(f"Answer Correctness: {correctness_avg:.2f} ({len(correctness_scores)} samples)")
        
    if "answer_relevancy_tests" in dataset:
        relevancy_scores, relevancy_details = results.pop(0)
        relevancy_avg = sum(relevancy_scores) / len(relevancy_scores)
        scores["Answer Relevancy"] = relevancy_avg
        all_details.extend(relevancy_details)
        if verbose:
            print(f"Answer Relevancy: {relevancy_avg:.2f} ({len(relevancy_scores)} samples)")
            
    if "acknowledge_contradiction_tests" in dataset:
        contradictions_scores, contradictions_details = results.pop(0)
        contradictions_avg = sum(contradictions_scores) / len(contradictions_scores)
        scores["Contradiction Acknowledgment"] = contradictions_avg
        all_details.extend(contradictions_details)
        if verbose:
            print(f"Contradiction Acknowledgment: {contradictions_avg:.2f} ({len(contradictions_scores)} samples)")
            
    if "citations_real_and_used_tests" in dataset:
        citations_scores, citations_details = results.pop(0)
        citations_avg = sum(citations_scores) / len(citations_scores)
        scores["Citations Real and Used"] = citations_avg
        all_details.extend(citations_details)
        if verbose:
            print(f"Citations Real and Used: {citations_avg:.2f} ({len(citations_scores)} samples)")
    
    # Calculate overall score
    all_scores = []
    if "faithfulness_tests" in dataset:
        all_scores.extend(faithfulness_scores)
    if "answer_correctness_tests" in dataset:
        all_scores.extend(correctness_scores)
    if "answer_relevancy_tests" in dataset:
        all_scores.extend(relevancy_scores)
    if "acknowledge_contradiction_tests" in dataset:
        all_scores.extend(contradictions_scores)
    if "citations_real_and_used_tests" in dataset:
        all_scores.extend(citations_scores)
    
    overall_score = sum(all_scores) / len(all_scores)
    scores["Overall"] = overall_score
    
    if verbose:
        print(f"\nOverall Score: {overall_score:.2f} ({len(all_scores)} total samples)")
        
    return scores, all_details

if __name__ == "__main__":
    evaluate_response_generator(verbose=True) 