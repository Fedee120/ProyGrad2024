PROMPT = """You are evaluating if a context passage contains key information from a ground truth answer.

Follow these steps:
1. Analyze the query and ground truth answer to identify key pieces of information
2. Check if the context contains these key pieces of information
3. Explain your reasoning step by step
4. Conclude if the context contains significant key information from the ground truth following the structured output format.

For example:
Query: "What is deep learning?"
Context: "Deep learning is a subset of machine learning that uses neural networks with multiple layers. It has revolutionized computer vision."
Ground Truth: "Deep learning is a subset of machine learning that uses neural networks with multiple layers. These networks automatically learn hierarchical representations of data. Deep learning has revolutionized fields like computer vision and NLP by automatically discovering features needed for classification."

Reasoning:
- Key information from ground truth:
   - Deep learning
   - Machine learning
   - Neural networks
   - Multiple layers
   - Hierarchical representations
   - Computer vision
   - NLP
- Found information in context:
   - Deep learning
   - Machine learning
   - Neural networks
   - Multiple layers
   - Computer vision
- Result: true (The context contains significant key information despite missing some details)

Another example:
Query: "What is deep learning?"
Context: "The weather today is sunny with mild temperatures. Perfect for outdoor activities."
Ground Truth: "Deep learning is a subset of machine learning that uses neural networks with multiple layers. These networks automatically learn hierarchical representations of data. Deep learning has revolutionized fields like computer vision and NLP."

Reasoning:
- Key information from ground truth:
   - Deep learning
   - Machine learning
   - Neural networks
   - Multiple layers
   - Hierarchical representations
   - Computer vision
   - NLP
- Information found in the context:
   - None
- Result: false (The context contains no relevant information)

Query: {query}
Context: {context}
Ground Truth: {ground_truth}

Analyze if this context contains key information from the ground truth answer. Follow the structured output format.""" 