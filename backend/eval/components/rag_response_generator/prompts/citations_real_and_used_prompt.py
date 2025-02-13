PROMPT = """You are a teacher grading if a student's context pieces used to answer a question are both real (present in the provided context pieces) and actually used in the answer (present in the context pieces used).

Follow these steps:
1. Review all the context pieces used listed below
2. Check if each of those context pieces used exists in the provided context pieces
3. Verify if each of those context pieces used are effectively used in the answer
4. Explain your reasoning step by step
5. Conclude if all context pieces used are both real and used following the structured output format.

For example:
- If a context piece used is not present in the answer, its bad
- If a context piece used is not present in the provided context pieces, its bad
- If a context piece used is present in the answer and it's present in the context pieces, its good
- If the answer uses information but doesn't have a corresponding context piece used, that's fine (we're only checking citations are real and used)
- If the answer doesn't clearly mentions the information comes from the context piece used, that's fine (we're only checking citations are real and used)

Provided context pieces:
{context}

Question: {question}
Answer: {answer}
Context pieces used: {citations}
Evaluate if all context pieces used are both real and used and provide your response in the specified JSON format.""" 
