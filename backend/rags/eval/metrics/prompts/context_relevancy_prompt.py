PROMPT = """You are a teacher determining if a single excerpt of a document is relevant or not for answering a specific question.
                    Follow these steps:
                    1. Analyze the context carefully
                    2. Determine if the context helps answer the question directly or provides important related information
                    3. Explain your reasoning step by step
                    4. Conclude with true if the context is relevant, or false if it is not

                    Question: {question}
                    Context to analyze: {context}
                    Is this context relevant? Answer with true or false.""" 