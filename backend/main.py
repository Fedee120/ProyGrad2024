from fastapi import FastAPI, HTTPException, Depends, Request, File, UploadFile
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
import openai
import tempfile

load_dotenv()  # Load environment variables

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

@app.post("/transcribe-audio")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    try:
        # Crear un archivo temporal para guardar el audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
            # Escribir el contenido del archivo subido al temporal
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Transcribir el audio usando Whisper
            client = openai.OpenAI()
            with open(temp_file_path, "rb") as audio:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    language="es"
                )
            
            # Eliminar el archivo temporal
            os.unlink(temp_file_path)
            
            return {"text": transcript.text}
        except Exception as e:
            # Asegurarse de eliminar el archivo temporal en caso de error
            os.unlink(temp_file_path)
            raise e
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8090)
