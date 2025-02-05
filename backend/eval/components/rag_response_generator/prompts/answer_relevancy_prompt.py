PROMPT = """You are evaluating if a response generator's answer is relevant to the question asked, given a specific context.
The context may be invented to test the response generator's ability to answer the question using the information from this context.
The context might not be relevant to the question, in those cases a relevant answer should acknowledge there's no information.

Follow these steps:
1. Analyze the question in light of this context
2. Determine if the main point of the question was addressed by the answer
3. Explain your reasoning step by step
4. Conclude with true if the answer addresses the question using the given context's framework, or false if it does not

Context:
{context}

Question: {question}
Answer: {answer}

Is the answer relevant to the question given this context? Answer with true or false.""" 