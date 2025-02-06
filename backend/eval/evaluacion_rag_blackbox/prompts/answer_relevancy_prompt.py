PROMPT = """You are a teacher determining if a student's answer is relevant to the question asked.
                    Follow these steps:
                    1. Analyze the question carefully
                    2. Review the answer and its relationship to the question
                    3. Explain your reasoning step by step
                    4. Conclude with true if the answer is relevant to the question, or false if it is not

                    Question: {question}
                    Answer: {answer}
                    Is the answer relevant? Answer with true or false.""" 