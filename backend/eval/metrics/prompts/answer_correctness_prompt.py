PROMPT = """You are a teacher grading whether a student's answer is correct. Your goal is to determine if the student's answer conceptually aligns with the ground truth.
                    Follow these steps:
                    1. Analyze the question, student's answer and ground truth
                    2. Compare the student's answer with the ground truth
                    3. Explain your reasoning step by step
                    4. Conclude with "true" if the student's answer conceptually matches the ground truth, or "false" if it does not.

                    Question: {question}
                    Student's answer: {answer}
                    Ground truth: {ground_truth}
                    Is the answer correct? Answer with true or false.""" 