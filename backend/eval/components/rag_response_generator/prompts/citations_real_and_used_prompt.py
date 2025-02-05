PROMPT = """You are evaluating if a response generator's citations are both real (present in the provided context) and actually used in the answer.

Follow these steps:
1. Review all the Citations listed below
2. Check if each of those citations exists in the provided context
3. Verify if each of those citations is used in the answer
4. Explain your reasoning step by step
5. Conclude with true only if ALL citations are both real and used, false otherwise

For example:
- If a citation is not present in the answer, its bad
- If a citation is not present in the provided context, its bad
- If a citation is present in the answer and it's present in the context, its good
- If the answer uses information but doesn't cite its source, that's fine (we're only checking citations are real and used)
- If the answer doesn't clearly mentions the information comes from the citation, that's fine (we're only checking citations are real and used)

Context:
{context}

Question: {question}
Answer: {answer}
Citations: {citations}
Are all citations real and properly used? Answer with true or false.""" 