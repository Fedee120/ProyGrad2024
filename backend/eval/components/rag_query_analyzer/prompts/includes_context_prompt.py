PROMPT = """You are evaluating if a query analyzer correctly considers the conversation context when generating/updating queries. The query analyzer should generate updates the original query and also expands into subqueries to increase the coverage of the original query.

Follow these steps:
1. Review the conversation history to understand the context
2. Check if the generated queries incorporate relevant information from the context
3. Compare the generated queries with the expected queries to ensure similar coverage
4. Verify if the updated query properly expands the user's question with context
5. Explain your reasoning step by step
6. Conclude with true if the queries show clear consideration of context, false if not

For example:
... previous conversation history ...
User: He leído que los modelos de lenguaje pueden producir información incorrecta e inventar contenido al generar texto.
AI: Es cierto, algunos modelos de lenguaje pueden generar información imprecisa o sesgada, lo cual puede deberse a varios factores relacionados con los datos, el diseño del modelo y su entrenamiento.
User: Entonces, ¿deberíamos desconfiar de la inteligencia artificial?

Output queries: 
- "Ethical concerns on AI trust"
- "Accuracy of AI-generated text"
- "Trustworthiness of language models in content generation"
Output updated query: "¿Deberíamos desconfiar de la inteligencia artificial debido a los riesgos de producir información incorrecta e inventar contenido al generar texto?"

Conversation History:
{chat_history}

Original Query: {original_query}
Expected Queries: {expected_queries}
Generated Queries: {queries}
Updated Query: {updated_query}

Do the generated queries and the updated query show consideration of conversation context? Follow the structured output format.""" 