from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from agents.agent import Agent

app = FastAPI()

class MessageRequest(BaseModel):
    message: str

@app.get("/check_status")
async def check_status():
    return JSONResponse(content=_generate_content(True))

@app.post("/invoke_agent")
def invoke_agent(request: MessageRequest):
    try:
        agent = Agent()
        response = agent.invoke({"input": request.message})
        return JSONResponse(content=_generate_content(True, data=response))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def _generate_content(success: bool, data: dict = None, error: dict = None):
    status = "success" if success else "fail"
    if error is not None:
        status = "error"
    content = {
        "status": status,
        "message": "An error occurred" if error else "Request completed successfully"
    }
    if data:
        content["data"] = data
    if error:
        content["error"] = error
    return content

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

# Example JSON Response Structures:
# Success Response:
# {
#   "status": "success",
#   "message": "Request completed successfully",
#   "data": {
#     "key1": "value1",
#     "key2": "value2"
#   }
# }
# Error Response:
# {
#   "status": "error",
#   "message": "An error occurred",
#   "error": {
#     "code": 400,
#     "details": "Invalid request parameters"
#   }
# }