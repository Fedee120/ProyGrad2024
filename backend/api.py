from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from run import run_graph
from typing import Optional, List, Set
from checkpointer import MongoDBCheckpointer

app = FastAPI(title="Sistema RAG Adaptativo")
checkpointer = MongoDBCheckpointer()

class Question(BaseModel):
    question: str
    thread_id: Optional[str] = None

class Response(BaseModel):
    thread_id: str
    response: str
    useful_docs: List[str]

class ThreadDocuments(BaseModel):
    thread_id: str
    documents: Set[str]

@app.post("/chat", response_model=Response)
async def chat(question: Question):
    try:
        # Si no se proporciona thread_id, crear uno nuevo
        thread_id = question.thread_id or str(uuid.uuid4())
        
        # Ejecutar el grafo RAG
        response, useful_docs = run_graph(question=question.question, thread_id=thread_id)
        
        return Response(
            thread_id=thread_id,
            response=response,
            useful_docs=useful_docs
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/thread/{thread_id}/documents", response_model=ThreadDocuments)
async def get_thread_documents(thread_id: str):
    """
    Obtiene todos los documentos útiles únicos usados en una conversación.
    """
    try:
        documents = checkpointer.get_thread_documents(thread_id)
        return ThreadDocuments(
            thread_id=thread_id,
            documents=documents
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8085) 