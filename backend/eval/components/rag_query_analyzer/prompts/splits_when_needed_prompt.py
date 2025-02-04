PROMPT = """You are an expert at evaluating query analysis systems.

Analyze if the query analyzer correctly decided whether to split the original query into multiple search queries.

Original Query: {original_query}
Generated Queries: {generated_queries}
Expected Queries: {expected_queries}

Your task is to evaluate ONLY if the analyzer correctly decided to split the query into multiple queries. 
Do NOT consider other types of query modifications (like acronym expansion or reference resolution) in your evaluation.

A query should be split into multiple queries ONLY when:
1. The original query contains multiple distinct questions or aspects that would be better searched separately
2. Searching for all aspects together in a single query would likely reduce retrieval quality
3. Resulting splitted queries are the MINIMAL amount needed to correctly separate different aspects of the original query

Examples of when splitting is needed:
- "What is X and what are its applications?" → Should split into ["what is X", "applications of X"]
- "Compare the advantages and disadvantages of Y" → Should split into ["advantages of Y", "disadvantages of Y"]

Examples of when splitting is NOT needed:
- "What is the relationship between A and B?" → Single query is better
- "How does X work in the context of Y?" → Single query is better
- Simple questions with a single focus → Keep as one query

Output a structured analysis with:
- Detailed reasoning steps focusing only on the splitting decision
- Whether the splitting decision matches the expected output (both in terms of whether to split and how to split)""" 