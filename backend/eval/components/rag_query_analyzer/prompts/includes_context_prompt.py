PROMPT = """You are evaluating if a query analyzer correctly considers the conversation history when generating/updating queries. The query analyzer updates the original query and also expands into subqueries to increase the coverage of the original query.

Follow these steps:
1. Review the conversation history to understand the context
2. Check if the generated queries and updated query incorporate relevant information from the context
3. Compare the generated queries and updated query with the expected queries and expected updated query to ensure similar coverage
4. Explain your reasoning step by step
5. Conclude if the queries incorporate relevant information from the context following the structured output format.

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
Expected Updated Query: {expected_updated_query}
Generated Queries: {queries}
Updated Query: {updated_query}

Evaluate the context consideration and provide your response in the specified JSON format.""" 