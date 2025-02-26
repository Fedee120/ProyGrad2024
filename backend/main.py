from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import uvicorn
from firebase_admin import auth, credentials, initialize_app, get_app
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from agent.router import Router
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
from typing import List, Optional
from datetime import datetime, timezone
import uuid

load_dotenv()  # Load environment variables

environment = os.getenv("ENVIRONMENT")
is_production = environment == "prod"
if is_production:
    os.environ["LANGCHAIN_PROJECT"] = "ProyGrad2024"
else:
    os.environ["LANGCHAIN_PROJECT"] = f"ProyGrad2024 ({environment} - {os.getenv('DEVELOPER', 'Anonymous')})"
os.environ["LANGCHAIN_TRACING_V2"] = "true"

# Initialize Firebase Admin
try: # Try to get existing app
    firebase_app = get_app()
except ValueError: # If no app exists, initialize with credentials
    cred = credentials.Certificate("firebase-credentials.json")
    firebase_app = initialize_app(cred)

app = FastAPI()
router = Router()

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

# @app.get("/public/reload_data")
# async def public_reload_data():
#     try:
#         rag = RAG(URI=os.getenv("MILVUS_STANDALONE_URL"), COLLECTION_NAME="real_collection", search_kwargs={"k": 5}, search_type="mmr", embeddings_model_name="text-embedding-3-small")
#         rag.delete_all_documents()
#         load_data(rag)
#         return JSONResponse(content={"detail": "Data reloaded"})
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

class MessageRequest(BaseModel):
    message: str
    history: list[dict] = []
    threadId: str

class Citation(BaseModel):
    """APA-formatted citation for a document"""
    text: str  # The formatted APA citation text
    source: str  # The source filename
    title: Optional[str] = None  # The document title
    author: Optional[str] = None  # The document author
    year: Optional[str] = None  # The publication year

class MessageResponse(BaseModel):
    id: str
    timestamp: str
    response: str
    citations: list[Citation] = []

@app.post("/invoke_agent", response_model=MessageResponse)
async def invoke_agent(
    request: MessageRequest,
    user = Depends(verify_firebase_token)
):
    try:
        id = str(uuid.uuid4())
        response, citations = router.process_query(
            request.message,
            _format_history_messages(request.history),
            langsmith_extra={
                "metadata": {
                    "email": user["email"],
                    "thread_id": request.threadId,
                    "message_id": id,
                    "app_version": os.getenv("APP_VERSION") if os.getenv("APP_VERSION") else "unknown"
                }
            }
        )
        
        return MessageResponse(
            id=id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            response=response,
            citations=citations
        )
    except Exception as e:
        if is_production:
            raise HTTPException(status_code=500, detail=f"Ha ocurrido un error al procesar su solicitud.")
        else:
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
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8090,
        reload=True,           # Enable auto-reload
        reload_dirs=["./"],    # Watch the current directory for changes
    )
