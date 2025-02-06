PROMPT = """You are evaluating if a query analyzer's output considers the conversation context when generating queries.

Follow these steps:
1. Review the conversation history to understand the context
2. Check if the generated queries incorporate relevant information from the context
3. Verify if the updated query properly expands the user's question with context
4. Explain your reasoning step by step
5. Conclude with true if the queries show clear consideration of context, false if not

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

------------------------------------------------------------------------------------------------

Conversation History:
{chat_history}

Original Query: {original_query}
Generated Queries: {queries}
Updated Query: {updated_query}

Do the queries show consideration of conversation context? Answer with true or false.""" 