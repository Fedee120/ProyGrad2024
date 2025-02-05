from .metrics.answer_correctness import evaluate_answer_correctness
from .metrics.answer_relevancy import evaluate_answer_relevancy
from .metrics.faithfulness import evaluate_faithfulness
from .metrics.acknowledge_contradiction import evaluate_acknowledge_contradiction
from agent.llms.rag_response_generator import RAGResponseGenerator
from tqdm import tqdm
import json
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

def evaluate_faithfulness_samples(
    generator: RAGResponseGenerator,
    samples: List[Dict[str, Any]],
    verbose: bool = False
) -> List[float]:
    """
    Evaluate if generated answers only use information from the provided context.
    Tests if the model is faithful to the given context and doesn't add external information.
    """
    scores = []
    for sample in samples:
        # Generate answer using the provided context
        generated_answer = generator.generate_response(
            question=sample["question"],
            search_results=sample["context"]
        )
        
        # Evaluate if the answer only uses information from the context
        score = evaluate_faithfulness(
            question=sample["question"],
            facts=sample["context"],
            answer=generated_answer.answer,
            verbose=verbose
        )
        
        if verbose:
            print(f"\nEvaluating faithfulness for: {sample['question']}")
            print(f"Context provided: {sample['context']}")
            print(f"Generated answer: {generated_answer}")
            print(f"Score: {score:.2f}")
        scores.append(score)
    return scores

def evaluate_correctness_samples(
    generator: RAGResponseGenerator,
    samples: List[Dict[str, Any]],
    verbose: bool = False
) -> List[float]:
    """
    Evaluate if generated answers match expected answers.
    Tests if the model generates answers that are semantically equivalent to expected answers.
    The model receives context but is evaluated on answer correctness regardless of context usage.
    """
    scores = []
    for sample in samples:
        # Generate answer with context
        generated_answer = generator.generate_response(
            question=sample["question"],
            search_results=sample["context"]
        )
        
        # Compare generated answer with expected answer
        score = evaluate_answer_correctness(
            question=sample["question"],
            answer=generated_answer.answer,
            ground_truth=sample["expected_answer"],
            verbose=verbose
        )
        
        if verbose:
            print(f"\nEvaluating correctness for: {sample['question']}")
            print(f"Context provided: {sample['context']}")
            print(f"Generated answer: {generated_answer}")
            print(f"Expected answer: {sample['expected_answer']}")
            print(f"Score: {score:.2f}")
        scores.append(score)
    return scores

def evaluate_relevancy_samples(
    generator: RAGResponseGenerator,
    samples: List[Dict[str, Any]],
    verbose: bool = False
) -> List[float]:
    """
    Evaluate if generated answers are relevant to the questions asked.
    Tests if the model's answers actually address what was asked using the context's framework.
    The model receives context and is evaluated on answer relevancy within that context.
    """
    scores = []
    for sample in samples:
        # Generate answer with context
        generated_answer = generator.generate_response(
            question=sample["question"],
            search_results=sample["context"]
        )
        
        # Check if answer is relevant to the question within the given context
        score = evaluate_answer_relevancy(
            question=sample["question"],
            answer=generated_answer.answer,
            context=sample["context"],
            verbose=verbose
        )
        
        if verbose:
            print(f"\nEvaluating relevancy for: {sample['question']}")
            print(f"Context provided: {sample['context']}")
            print(f"Generated answer: {generated_answer}")
            print(f"Score: {score:.2f}")
        scores.append(score)
    return scores

def evaluate_contradiction_samples(
    generator: RAGResponseGenerator,
    samples: List[Dict[str, Any]],
    verbose: bool = False
) -> List[float]:
    """
    Evaluate if generated answers acknowledge contradictions in the context when present.
    Tests if the model identifies and mentions conflicting information from different sources.
    """
    scores = []
    for sample in samples:
        # Generate answer with context
        generated_answer = generator.generate_response(
            question=sample["question"],
            search_results=sample["context"]
        )
        
        # Check if answer acknowledges contradictions when present
        score = evaluate_acknowledge_contradiction(
            question=sample["question"],
            answer=generated_answer.answer,
            context=sample["context"],
            verbose=verbose
        )
        
        if verbose:
            print(f"\nEvaluating contradiction acknowledgment for: {sample['question']}")
            print(f"Context provided: {sample['context']}")
            print(f"Generated answer: {generated_answer}")
            print(f"Score: {score:.2f}")
        scores.append(score)
    return scores

if __name__ == "__main__":
    load_dotenv()
    
    generator = RAGResponseGenerator()
    
    # Load test dataset
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(current_dir, "datasets", "response_generator_dataset.json")
    
    with open(dataset_path, encoding="utf-8") as f:
        dataset = json.load(f)
    
    # Process each test set in parallel
    with ThreadPoolExecutor() as executor:
        futures = []
        
        if "faithfulness_tests" in dataset:
            futures.append(
                executor.submit(
                    evaluate_faithfulness_samples,
                    generator,
                    dataset["faithfulness_tests"],
                    True
                )
            )
        
        if "answer_correctness_tests" in dataset:
            futures.append(
                executor.submit(
                    evaluate_correctness_samples,
                    generator,
                    dataset["answer_correctness_tests"],
                    True
                )
            )
        
        if "answer_relevancy_tests" in dataset:
            futures.append(
                executor.submit(
                    evaluate_relevancy_samples,
                    generator,
                    dataset["answer_relevancy_tests"],
                    True
                )
            )
            
        if "acknowledge_contradiction_tests" in dataset:
            futures.append(
                executor.submit(
                    evaluate_contradiction_samples,
                    generator,
                    dataset["acknowledge_contradiction_tests"],
                    True
                )
            )
        
        # Get results
        results = [future.result() for future in futures]
    
    # Calculate scores for each metric
    if "faithfulness_tests" in dataset:
        faithfulness_scores = results.pop(0)
        faithfulness_avg = sum(faithfulness_scores) / len(faithfulness_scores)
        print(f"\nFaithfulness: {faithfulness_avg:.2f} ({len(faithfulness_scores)} samples)")
    
    if "answer_correctness_tests" in dataset:
        correctness_scores = results.pop(0)
        correctness_avg = sum(correctness_scores) / len(correctness_scores)
        print(f"Answer Correctness: {correctness_avg:.2f} ({len(correctness_scores)} samples)")
    
    if "answer_relevancy_tests" in dataset:
        relevancy_scores = results.pop(0)
        relevancy_avg = sum(relevancy_scores) / len(relevancy_scores)
        print(f"Answer Relevancy: {relevancy_avg:.2f} ({len(relevancy_scores)} samples)")
        
    if "acknowledge_contradiction_tests" in dataset:
        contradiction_scores = results.pop(0)
        contradiction_avg = sum(contradiction_scores) / len(contradiction_scores)
        print(f"Contradiction Acknowledgment: {contradiction_avg:.2f} ({len(contradiction_scores)} samples)")
    
    # Calculate overall score
    all_scores = []
    if "faithfulness_tests" in dataset:
        all_scores.extend(faithfulness_scores)
    if "answer_correctness_tests" in dataset:
        all_scores.extend(correctness_scores)
    if "answer_relevancy_tests" in dataset:
        all_scores.extend(relevancy_scores)
    if "acknowledge_contradiction_tests" in dataset:
        all_scores.extend(contradiction_scores)
    
    overall_score = sum(all_scores) / len(all_scores)
    print(f"\nOverall Score: {overall_score:.2f} ({len(all_scores)} total samples)") 