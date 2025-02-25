from metrics.context_recall import evaluate_context_recall, extract_statements, evaluate_context_coverage

def test_context_recall():
    print("Testing Context Recall Metric with Two-Stage Approach")
    print("=" * 80)

    # Example data
    query = "What is deep learning?"
    ground_truth = "Deep learning is a subset of machine learning that uses neural networks with multiple layers. These networks automatically learn hierarchical representations of data, transforming inputs into increasingly abstract representations. Deep learning has revolutionized fields like computer vision and natural language processing by automatically discovering features needed for classification or prediction, eliminating manual feature engineering."
    
    contexts = [
        "Deep learning is a subset of machine learning that uses neural networks with multiple layers.",
        "Neural networks in deep learning learn hierarchical representations of data, transforming raw inputs into abstract features.",
        "Deep learning has revolutionized the field of computer vision and object recognition.",
        "The weather is sunny today and the temperature is mild. Perfect for outdoor activities.",
        "Natural language processing has been transformed by deep learning approaches that automatically discover features from text data."
    ]
    
    # Step 1: Test statement extraction
    print("\n1. Testing Statement Extraction")
    print("-" * 80)
    statements = extract_statements(query, ground_truth, verbose=True)
    
    # Step 2: Test context coverage evaluation for a single context
    print("\n2. Testing Context Coverage Evaluation")
    print("-" * 80)
    context = contexts[0]  # Use the first context for testing
    context, coverage_assessments, coverage_counts = evaluate_context_coverage(
        query, context, statements, verbose=True
    )
    
    # Step 3: Test full context recall evaluation
    print("\n3. Testing Full Context Recall Evaluation")
    print("-" * 80)
    recall_score, detailed_results = evaluate_context_recall(
        query, contexts, ground_truth, verbose=True
    )
    
    print("\nTest Completed Successfully")
    print(f"Final Recall Score: {recall_score:.2f}")
    print(f"Weighted Recall Score: {detailed_results['weighted_recall_score']:.2f}")
    
if __name__ == "__main__":
    test_context_recall() 