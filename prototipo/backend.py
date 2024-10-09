import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from langchain_community.chat_message_histories import ChatMessageHistory

from rag_agent import RagAgent  # Importar RagAgent desde rag_agent.py

app = FastAPI()

# Almacena el historial de chat por sesión como ChatMessageHistory
session_histories: Dict[str, ChatMessageHistory] = {}

class QueryRequest(BaseModel):
    session_id: str
    query: str

class QueryResponse(BaseModel):
    response: str

@app.post("/chat", response_model=QueryResponse)
def chat(request: QueryRequest):
    session_id = request.session_id
    query = request.query

    # Obtener el historial de la sesión o crear uno nuevo
    chat_history = session_histories.get(session_id)
    if not chat_history:
        chat_history = ChatMessageHistory()
        session_histories[session_id] = chat_history

    # Crear una instancia de RagAgent
    agent = RagAgent(session_id=session_id, chat_history=chat_history)

    if not agent.has_credentials():
        raise HTTPException(status_code=500, detail="Credenciales no configuradas.")

    # Interactuar con el agente
    response_text = agent.interact_with_agent(query)

    # Actualizar el historial de la sesión utilizando los métodos de ChatMessageHistory
    chat_history.add_user_message(query)
    chat_history.add_ai_message(response_text)

    return QueryResponse(response=response_text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
