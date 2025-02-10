PROMPT = """You are evaluating if a query analyzer correctly resolves references from the chat history in the query.

Evaluate if the references in the original query were resolved correctly by comparing the generated query with the expected query.
Focus specifically on how pronouns and references were resolved to their full meanings based on the chat history context.

Consider:
- Pronouns (it, they, them, etc.)
- Demonstrative references (this, that, these, those)
- Implicit references to previously discussed topics
- Whether the resolution maintains the original meaning and intent

Output a structured analysis with:
- Detailed reasoning steps explaining how references were resolved
- Whether the reference resolutions match the expected output

Chat History:
{chat_history}

Original Query: {original_query}
Generated Query: {generated_query}
Expected Query: {expected_query}

Are references resolved correctly? Follow the structured output format.""" 
