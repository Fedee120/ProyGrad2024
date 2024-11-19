from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import uvicorn
from firebase_admin import auth, credentials, initialize_app
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from agent.orchestrator import ChatOrchestrator
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
from typing import List
from data.load_data import load_data
from rags.openai.rag import RAG
import mlflow

load_dotenv()  # Load environment variables

# Using a local MLflow tracking server
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))

# Create a new experiment that the model and the traces will be logged to
mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT"))

# Inicializar Firebase Admin
cred = credentials.Certificate("firebase-credentials.json")
firebase_app = initialize_app(cred)

app = FastAPI()

# Split the CORS_ORIGINS string into a list
origins = os.getenv("CORS_ORIGINS").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Now using the origins from environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

async def verify_firebase_token(request: Request, token: HTTPBearer = Depends(security)):
    try:
        decoded_token = auth.verify_id_token(token.credentials)
        request.state.user_id = decoded_token['uid']
        return decoded_token
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token is invalid or expired"
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}"
        )

@app.get("/public/reload_data")
async def public_reload_data():
    try:
        rag = RAG(URI=os.getenv("MILVUS_STANDALONE_URL"), COLLECTION_NAME="real_collection", search_kwargs={"k": 5}, search_type="mmr", embeddings_model_name="text-embedding-3-small")
        rag.delete_all_documents()
        load_data(rag)
        return JSONResponse(content={"detail": "Data reloaded"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/check_status")
async def check_status(user = Depends(verify_firebase_token)):
    return JSONResponse(content={"detail": "Backend is up and running"})

class MessageRequest(BaseModel):
    message: str
    history: list[dict] = []

class MessageResponse(BaseModel):
    response: str
    citations: list[str] = []

@app.post("/invoke_agent", response_model=MessageResponse)
async def invoke_agent(
    request: MessageRequest,
    user = Depends(verify_firebase_token)
):
    try:
        orchestrator = ChatOrchestrator()
        response, citations, _ = orchestrator.process_query(
            request.message,
            _format_history_messages(request.history)
        )
        
        return MessageResponse(
            response=response,
            citations=citations
        )
    except Exception as e:
        if "request" in e.__dict__:
            raise HTTPException(status_code=500, detail=f"{e.__dict__['request']} {str(e)}")
        else:
            raise HTTPException(status_code=500, detail=str(e))
        
def _format_history_messages(history: List[dict]) -> List[BaseMessage]:
    """Convert chat history into a list of messages."""
    if not history:
        return []
    
    formatted_messages = []
    for msg in history:
        if msg["role"] == "user":
            formatted_messages.append(HumanMessage(content=msg["content"]))
        else:
            formatted_messages.append(AIMessage(content=msg["content"]))
    
    return formatted_messages

if __name__ == "__main__":
    # Enable LangChain autologging
    # Note that models and examples are not required to be logged in order to log traces.
    # Simply enabling autolog for LangChain via mlflow.langchain.autolog() will enable trace logging.
    mlflow.langchain.autolog(log_models=True, log_input_examples=True) # Done only in development to avoid logging the model interactions in production

    uvicorn.run(app, host="0.0.0.0", port=8090)
