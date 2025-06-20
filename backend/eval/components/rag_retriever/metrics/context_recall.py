from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import List, Tuple, Dict, Any, Literal
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..prompts.context_recall_prompt import STATEMENT_EXTRACTION_PROMPT, STATEMENT_COVERAGE_PROMPT

load_dotenv()

class Statement(BaseModel):
    """A single factual statement extracted from the ground truth."""
    content: str = Field(..., description="The factual statement text")

class StatementExtraction(BaseModel):
    """Container for extracted statements from ground truth."""
    statements: List[Statement] = Field(..., description="List of factual statements extracted from the ground truth")

class StatementCoverage(BaseModel):
    """Coverage assessment for a single statement."""
    statement: str = Field(..., description="The statement being evaluated")
    coverage: Literal["full", "partial", "none"] = Field(..., description="Coverage level of the statement")
    reasoning: str = Field(..., description="Reasoning for the coverage assessment")

class ContextCoverage(BaseModel):
    """Coverage assessment for all statements in a context."""
    coverage_assessments: List[StatementCoverage] = Field(..., description="Coverage assessment for each statement")

def extract_statements(
    query: str,
    ground_truth: str,
    verbose: bool = False
) -> List[str]:
    """
    Extract distinct factual statements from the ground truth.
    
    Args:
        query: The search query
        ground_truth: The ground truth answer to break down
        verbose: Whether to print detailed extraction information
        
    Returns:
        List[str]: List of extracted statements
    """
    prompt = STATEMENT_EXTRACTION_PROMPT.format(
        query=query,
        ground_truth=ground_truth
    )
    
    # Get structured output from LLM
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=5000)
    llm_structured = llm.with_structured_output(StatementExtraction)
    result = llm_structured.invoke(prompt)
    
    statements = [statement.content for statement in result.statements]
    
    if verbose:
        print("\nExtracted statements from ground truth:")
        for i, statement in enumerate(statements, 1):
            print(f"{i}. {statement}")
    
    return statements

def evaluate_context_coverage(
    query: str,
    context: str,
    statements: List[str],
    verbose: bool = False
) -> Tuple[str, List[StatementCoverage], Dict[str, int]]:
    """
    Evaluate how well a context covers the extracted statements.
    
    Args:
        query: The search query
        context: The context passage to evaluate
        statements: List of factual statements from the ground truth
        verbose: Whether to print detailed evaluation information
        
    Returns:
        Tuple[str, List[StatementCoverage], Dict[str, int]]: 
            - Context
            - Coverage assessments for each statement
            - Summary counts of coverage levels
    """
    formatted_statements = "\n".join([f"- {statement}" for statement in statements])
    
    prompt = STATEMENT_COVERAGE_PROMPT.format(
        query=query,
        context=context,
        statements=formatted_statements
    )
    
    # Get structured output from LLM
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=5000)
    llm_structured = llm.with_structured_output(ContextCoverage)
    result = llm_structured.invoke(prompt)
    
    # Count coverage levels
    coverage_counts = {
        "full": 0,
        "partial": 0,
        "none": 0
    }
    
    for assessment in result.coverage_assessments:
        coverage_counts[assessment.coverage] += 1
    
    if verbose:
        print(f"\nEvaluating context: {context}")
        print("\nCoverage assessments:")
        for i, assessment in enumerate(result.coverage_assessments, 1):
            print(f"{i}. \"{assessment.statement}\" - {assessment.coverage.upper()} - {assessment.reasoning}")
        print(f"\nCoverage summary: {coverage_counts['full']} full, {coverage_counts['partial']} partial, {coverage_counts['none']} none")
    
    return context, result.coverage_assessments, coverage_counts

def evaluate_context_recall(
    query: str,
    contexts: List[str],
    ground_truth: str,
    max_workers: int = 3,
    verbose: bool = False
) -> Tuple[float, Dict[str, Any]]:
    """
    Evaluate how well the retrieved contexts cover information from the ground truth.
    First extracts statements from ground truth, then evaluates coverage for each context.
    
    Args:
        query: The search query
        contexts: List of retrieved context passages
        ground_truth: The ground truth answer to compare against
        max_workers: Maximum number of concurrent evaluations
        verbose: Whether to print detailed evaluation information
        
    Returns:
        Tuple[float, Dict[str, Any]]: 
            - Recall score (proportion of statements covered across all contexts)
            - Detailed results including per-context evaluation
    """
    if not contexts or not ground_truth:
        return 0.0, {}
    
    # Step 1: Extract statements from ground truth
    statements = extract_statements(query, ground_truth, verbose)
    if not statements:
        raise ValueError("No se pudieron extraer afirmaciones")
    
    # Step 2: Evaluate coverage for each context
    context_results = []
    
    # Track best coverage for each statement
    best_statement_coverage = {statement: "none" for statement in statements}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create futures for each context
        future_to_context = {
            executor.submit(evaluate_context_coverage, query, ctx, statements, verbose): i 
            for i, ctx in enumerate(contexts, 1)
        }
        
        # Process results as they complete
        for future in as_completed(future_to_context):
            context_num = future_to_context[future]
            try:
                context, coverage_assessments, coverage_counts = future.result()
                
                # Update best coverage for each statement
                for assessment in coverage_assessments:
                    statement = assessment.statement
                    coverage = assessment.coverage
                    
                    # Update if better coverage is found
                    # (full > partial > none)
                    current_best = best_statement_coverage.get(statement, "none")
                    if current_best == "none" or (current_best == "partial" and coverage == "full"):
                        best_statement_coverage[statement] = coverage
                
                # Store context-level results
                context_results.append({
                    "context_num": context_num,
                    "context": context,
                    "coverage_assessments": [assessment.model_dump() for assessment in coverage_assessments],
                    "coverage_counts": coverage_counts
                })
                    
            except Exception as e:
                print(f"Error processing context {context_num}: {str(e)}")
    
    # Calculate overall recall score
    # A statement is considered recalled if it has at least partial coverage
    recalled_statements = sum(1 for coverage in best_statement_coverage.values() 
                             if coverage in ["full", "partial"])
    recall_score = recalled_statements / len(statements)
    
    # Calculate weighted recall score (full counts as 1.0, partial as 0.5)
    weighted_recall = sum(1.0 if coverage == "full" else 0.5 if coverage == "partial" else 0.0 
                         for coverage in best_statement_coverage.values()) / len(statements)
    
    # Prepare detailed results
    detailed_results = {
        "recall_score": recall_score,
        "weighted_recall_score": weighted_recall,
        "total_statements": len(statements),
        "statements": statements,
        "statement_coverage": best_statement_coverage,
        "per_context_results": context_results
    }

    if verbose:
        print("\nOverall statement coverage:")
        for i, (statement, coverage) in enumerate(best_statement_coverage.items(), 1):
            print(f"{i}. \"{statement}\" - {coverage.upper()}")
        print(f"\nRecall score: {recall_score:.2f} ({recalled_statements}/{len(statements)} statements covered)")
        print(f"Weighted recall score: {weighted_recall:.2f}")
    
    return recall_score, detailed_results

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