PROMPT = """You are evaluating if a response generator's answer is relevant to the question asked, given a specific context.
The context may be invented to test the response generator's ability to answer the question using the information from this context.

Follow these steps:
1. Review the provided context carefully
2. Analyze the question in light of this context
3. Check if the answer uses the context's framework to address the question
4. Explain your reasoning step by step
5. Conclude with true if the answer addresses the question using the given context's framework, or false if it does not

Context:
{context}

Question: {question}
Answer: {answer}

Is the answer relevant to the question given this context? Answer with true or false.""" 