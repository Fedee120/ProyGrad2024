PROMPT = """You are a teacher grading a student's answer. You need to determine if the answer can be logically derived from the given facts.
                    Follow these steps:
                    1. Analyze the question and answer carefully
                    2. Review each fact and its relationship to the answer
                    3. Explain your reasoning step by step
                    4. Conclude with true if the answer is faithful to the facts, or false if it contains information not supported by the facts

                    Question: {question}
                    Facts: {facts}
                    Answer: {answer}
                    Is the answer faithful? Follow the structured output format.""" 