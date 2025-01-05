from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import uvicorn
from firebase_admin import auth, credentials, initialize_app
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from typing import List
from run import run_graph
import uuid

load_dotenv()  # Load environment variables

environment = os.getenv("ENVIRONMENT")
is_production = environment == "prod"
if is_production:
    os.environ["LANGCHAIN_PROJECT"] = "ProyGrad2024"
else:
    os.environ["LANGCHAIN_PROJECT"] = f"ProyGrad2024 ({environment} - {os.getenv('DEVELOPER', 'Anonymous')})"

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
    threadId: str

class MessageResponse(BaseModel):
    response: str
    citations: list[str] = []

@app.post("/invoke_agent", response_model=MessageResponse)
async def invoke_agent(
    request: MessageRequest,
    user = Depends(verify_firebase_token)
):
    try:
        response, useful_docs = run_graph(
            question=request.message,
            thread_id=request.threadId,
            debug=not is_production
        )
        
        return MessageResponse(
            response=response,
            citations=useful_docs
        )
    except Exception as e:
        if is_production:
            raise HTTPException(status_code=500, detail=f"An error occurred while processing your request.")
        else:
            if "request" in e.__dict__:
                raise HTTPException(status_code=500, detail=f"{e.__dict__['request']} {str(e)}")
            else:
                raise HTTPException(status_code=500, detail=str(e))

@app.post("/test_agent")
async def test_agent(request: MessageRequest):
    try:
        response, useful_docs = run_graph(
            question=request.message,
            thread_id=request.threadId,
            debug=not is_production
        )
        
        return MessageResponse(
            response=response,
            citations=useful_docs
        )
    except Exception as e:
        if is_production:
            raise HTTPException(status_code=500, detail=f"An error occurred while processing your request.")
        else:
            if "request" in e.__dict__:
                raise HTTPException(status_code=500, detail=f"{e.__dict__['request']} {str(e)}")
            else:
                raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8090)
