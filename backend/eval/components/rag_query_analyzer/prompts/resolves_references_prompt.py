PROMPT = """You are evaluating if a query analyzer correctly resolves references from the chat history in the query. The query analyzer should generate updates the original query and also expands into subqueries to increase the coverage of the original query.

Follow these steps:
1. Identify any references (pronouns, demonstratives, implicit topics) in the original query
2. Review the chat history to understand what these references point to
3. Compare the updated query and the generated queries to see if references were properly resolved
4. Explain your reasoning step by step
5. Conclude with true if references were resolved correctly, false if not

Consider:
- Pronouns (it, they, them, etc.)
- Demonstrative references (this, that, these, those)
- Implicit references to previously discussed topics
- Whether the resolution maintains the original meaning and intent

Chat History:
{chat_history}

Original Query: {original_query}
Updated Query: {updated_query}
Generated Queries: {queries}

Are references resolved correctly? Follow the structured output format.""" 