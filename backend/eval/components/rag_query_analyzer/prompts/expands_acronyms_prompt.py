PROMPT = """You are evaluating if a query analyzer expands acronyms in at least one of its generated queries when acronyms are present.

Follow these steps:
1. Identify any acronyms in the original query
2. Check if at least one of the generated queries contains an expanded version of the acronym
3. Explain your reasoning step by step
4. Conclude if any acronym present is expanded in at least one query following the structured output format.

For example:
Original: "What is CNN?"
Queries: ["What is Convolutional Neural Network?", "What is CNN architecture?"]
Result: true (CNN is expanded to Convolutional Neural Network in one query)

Original: "How does a CPU work?"
Queries: ["How does a CPU work?", "CPU architecture explained"]
Result: false (CPU is not expanded to Central Processing Unit in one query)

Original: "What is deep learning?"
Queries: ["What is deep learning?", "Deep learning explained"]
Result: true (no acronyms present to expand)

Original Query: {original_query}
Generated Queries: {queries}

Evaluate the acronym expansion and provide your response in the specified JSON format.""" 
