PROMPT = """You are an expert at evaluating query analysis systems.

Analyze if the query analyzer correctly replaced acronyms in the query to enhance retrieval.

Original Query: {original_query}
Generated Query: {generated_query}
Expected Query: {expected_query}

Evaluate if the acronyms in the original query were replaced correctly by comparing the generated query with the expected query.
Focus specifically on how technical and domain-specific acronyms were expanded to their full forms.

Consider:
- Technical acronyms (ML, AI, NLP, etc.)
- Domain-specific abbreviations
- Whether the expansion maintains the original meaning

Output a structured analysis with:
- Detailed reasoning steps explaining how acronyms were handled
- Whether the acronym replacements match the expected output""" 