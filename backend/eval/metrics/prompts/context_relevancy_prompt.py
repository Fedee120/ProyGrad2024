PROMPT = """You are a teacher determining if a single excerpt of a document is relevant or not for answering a specific question.
                    Follow these steps:
                    1. Analyze the excerpt carefully
                    2. Determine if the excerpt helps answer the question directly or provides important related information
                    3. Explain your reasoning step by step
                    4. Conclude with true if the excerpt is relevant, or false if it is not

                    Question: {question}
                    Excerpt to analyze: {excerpt}
                    Is this excerpt relevant? Answer with true or false.""" 