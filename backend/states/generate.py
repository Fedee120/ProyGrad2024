### Generate

from langchain_openai import ChatOpenAI
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from typing import Dict
from langsmith import traceable

# Prompt
prompt = hub.pull("rlm/rag-prompt")

# LLM
llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Chain
rag_chain = prompt | llm | StrOutputParser()

@traceable(name="generate")
def generate(state: Dict) -> Dict:
    """
    Genera una respuesta utilizando el LLM basado en la pregunta y los documentos recuperados.
    
    Args:
        state (Dict): Estado actual del grafo.
    
    Returns:
        Dict: Contiene la generación realizada por el LLM.
    """
    question = state["question"]
    documents = state["documents"]
    message_history = state.get("message_history", [])  # Obtener historial de mensajes

    # Preparar el contexto para el LLM incluyendo el historial de mensajes
    prompt = ""
    for msg in message_history:
        if msg["user"] == "user":
            prompt += f"Usuario: {msg['message']}\n"
        else:
            prompt += f"Bot: {msg['message']}\n"
    prompt += f"Usuario: {question}\nBot:"

    llm = ChatOpenAI(model="gpt-3.5-turbo")
    generation = llm(prompt)

    return {"generation": generation}

