from pydantic.v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import List, Tuple, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..prompts.context_recall_prompt import PROMPT

load_dotenv()

class ContextRecall(BaseModel):
    reasoning_steps: List[str] = Field(..., description="List of reasoning steps explaining why the context does or does not contain key information from the ground truth")
    has_relevant_information: bool = Field(..., description="Indicates if the context contains key information from the ground truth")

def evaluate_single_context(
    query: str,
    context: str,
    ground_truth: str,
    verbose: bool = False
) -> Tuple[str, bool, List[str]]:
    """
    Evaluate if a single context passage contains key information from the ground truth.
    
    Args:
        query: The search query
        context: The context passage to evaluate
        ground_truth: The ground truth answer to compare against
        verbose: Whether to print detailed evaluation information
        
    Returns:
        Tuple[str, bool, List[str]]: 
            - Context
            - Whether it has relevant information
            - Reasoning steps
    """
    prompt = PROMPT.format(
        query=query,
        context=context,
        ground_truth=ground_truth
    )
    
    # Get structured output from LLM
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=5000)
    llm_structured = llm.with_structured_output(ContextRecall)
    result = llm_structured.invoke(prompt)
    
    if verbose:
        print(f"\nEvaluating context: {context}")
        print("\nReasoning steps:")
        for i, step in enumerate(result.reasoning_steps, 1):
            print(f"{i}. {step}")
        print(f"Has relevant information?: {result.has_relevant_information}")
    
    return context, result.has_relevant_information, result.reasoning_steps

def evaluate_context_recall(
    query: str,
    contexts: List[str],
    ground_truth: str,
    max_workers: int = 3,
    verbose: bool = False
) -> Tuple[float, Dict[str, Any]]:
    """
    Evaluate if the retrieved contexts contain key information from the ground truth.
    Each context is evaluated separately in parallel.
    
    Args:
        query: The search query
        context: List of retrieved context passages
        ground_truth: The ground truth answer to compare against
        max_workers: Maximum number of concurrent evaluations
        verbose: Whether to print detailed evaluation information
        
    Returns:
        Tuple[float, Dict[str, Any]]: 
            - Detailed results including per-context evaluation
    """
    if not contexts or not ground_truth:
        return 0.0, {}
    
    results = []
    relevant_contexts = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create futures for each context
        future_to_context = {
            executor.submit(evaluate_single_context, query, ctx, ground_truth, verbose): i 
            for i, ctx in enumerate(contexts, 1)
        }
        
        # Process results as they complete
        for future in as_completed(future_to_context):
            context_num = future_to_context[future]
            try:
                context, has_relevant_info, reasoning_steps = future.result()
                
                if has_relevant_info:
                    relevant_contexts += 1
                
                # Store context-level results
                results.append({
                    "context_num": context_num,
                    "context": context,
                    "has_relevant_information": has_relevant_info,
                    "reasoning_steps": reasoning_steps
                })
                    
                if verbose:
                    print(f"\nContext {context_num}:")
                    print(f"Content: {context}")
                    print("Reasoning steps:")
                    for i, step in enumerate(reasoning_steps, 1):
                        print(f"{i}. {step}")
                    print(f"Has relevant information?: {has_relevant_info}")
                    
            except Exception as e:
                print(f"Error processing context {context_num}: {str(e)}")
    
    # Calculate recall score (ratio of relevant contexts to total contexts)
    recall_score_best = min(relevant_contexts, 1)
    recall_score_all = relevant_contexts / len(contexts) if contexts else 0.0
    
    # Prepare detailed results
    detailed_results = {
        "recall_score_best": recall_score_best,
        "recall_score_all": recall_score_all,
        "total_contexts": len(contexts),
        "relevant_contexts": relevant_contexts,
        "per_context_results": results
    }

    if verbose:
        print(f"\nOverall recall score: {recall_score_best:.2f}")
        print(f"Relevant contexts: {relevant_contexts}/{len(contexts)}")
    
    return recall_score_best, detailed_results

if __name__ == "__main__":
    query = "What is deep learning?"
    contexts = [
        "Deep learning is a subset of machine learning that uses neural networks with multiple layers.",
        "It has revolutionized computer vision and natural language processing tasks.",
        "The weather is sunny today and the temperature is mild."
    ]
    ground_truth = "Deep learning is a subset of machine learning that uses neural networks with multiple layers. These networks automatically learn hierarchical representations of data, transforming inputs into increasingly abstract representations. Deep learning has revolutionized fields like computer vision and natural language processing by automatically discovering features needed for classification or prediction, eliminating manual feature engineering."
    score, details = evaluate_context_recall(query, contexts, ground_truth, verbose=True)
    print(f"\nFinal recall score: {score:.2f}") 