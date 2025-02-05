PROMPT = """You are evaluating if a response generator's answer acknowledges contradictions present in the provided context.
The model should explicitly mention when different sources provide conflicting information.

Follow these steps:
1. Review the provided context to identify any contradictions
2. Check if the answer acknowledges these contradictions
3. Explain your reasoning step by step
4. Conclude with true if the answer acknowledges contradictions when present, or false if it fails to do so

Context:
{context}

Question: {question}
Answer: {answer}

Does the answer acknowledge contradictions in the context when present? Answer with true or false.""" 