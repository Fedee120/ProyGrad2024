from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from agents.agent import Agent

app = FastAPI()

@app.get("/check_status")
async def check_status():
    return JSONResponse(content={"detail": "Backend is up and running"})

class MessageRequest(BaseModel):
    message: str

class MessageResponse(BaseModel):
    response: str

@app.post("/invoke_agent", response_model=MessageResponse)
def invoke_agent(request: MessageRequest):
    try:
        agent = Agent()
        result = agent.invoke({"input": request.message})
        response = result.get("output", "No response from agent")
        return MessageResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
