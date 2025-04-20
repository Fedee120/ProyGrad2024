STATEMENT_EXTRACTION_PROMPT = """You are an AI tasked with breaking down a ground truth answer into distinct factual statements or claims.

Follow these steps:
1. Analyze the query and ground truth answer carefully
2. Identify all distinct factual statements or claims made in the ground truth
3. List each statement as a separate, standalone fact
4. Ensure each statement represents a single, atomic piece of information

For example:
Query: "What is deep learning?"
Ground Truth: "Deep learning is a subset of machine learning that uses neural networks with multiple layers. These networks automatically learn hierarchical representations of data. Deep learning has revolutionized fields like computer vision and NLP by automatically discovering features needed for classification."

Statements:
- Deep learning is a subset of machine learning
- Deep learning uses neural networks with multiple layers
- These neural networks automatically learn hierarchical representations of data
- Deep learning has revolutionized computer vision
- Deep learning has revolutionized NLP
- Deep learning automatically discovers features needed for classification

Query: {query}
Ground Truth: {ground_truth}

Extract all distinct factual statements from this ground truth answer."""

STATEMENT_COVERAGE_PROMPT = """You are evaluating how well a context passage covers the factual statements from a ground truth answer.

Follow these steps:
1. Review each statement extracted from the ground truth
2. For each statement, determine if the context fully covers it, partially covers it, or doesn't cover it at all
3. Provide clear reasoning for your coverage assessment of each statement
4. Assign a coverage status for each statement: "full", "partial", or "none"

For example:
Query: "What is deep learning?"
Context: "Deep learning is a subset of machine learning that uses neural networks with multiple layers. It has revolutionized computer vision."
Statements:
- Deep learning is a subset of machine learning
- Deep learning uses neural networks with multiple layers
- These neural networks automatically learn hierarchical representations of data
- Deep learning has revolutionized computer vision
- Deep learning has revolutionized NLP
- Deep learning automatically discovers features needed for classification
- Deep learning eliminates the need for manual feature engineering

Coverage Assessment:
1. "Deep learning is a subset of machine learning" - FULL - The context explicitly states this
2. "Deep learning uses neural networks with multiple layers" - FULL - The context explicitly states this
3. "These neural networks automatically learn hierarchical representations of data" - NONE - Not mentioned in the context
4. "Deep learning has revolutionized computer vision" - FULL - The context explicitly states this
5. "Deep learning has revolutionized NLP" - NONE - NLP is not mentioned in the context
6. "Deep learning automatically discovers features needed for classification" - NONE - Not mentioned in the context
7. "Deep learning eliminates the need for manual feature engineering" - NONE - Not mentioned in the context

Query: {query}
Context: {context}
Statements:
{statements}

Evaluate how well this context covers each of the statements from the ground truth answer.""" 