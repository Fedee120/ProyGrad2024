from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.agent import Agent

app = FastAPI()

class MessageRequest(BaseModel):
    message: str

@app.post("/invoke_agent")
def invoke_agent(request: MessageRequest):
    try:
        agent = Agent()
        response = agent.invoke({"input": request.message})
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)