import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import run_agent

app = FastAPI()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]

class Recommendation(BaseModel):
    name: str
    url: str
    test_type: str

class ChatResponse(BaseModel):
    reply: str
    recommendations: list[Recommendation]
    end_of_conversation: bool

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        messages = [
            {"role": m.role, "content": m.content}
            for m in request.messages
        ]
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(None, run_agent, messages),
            timeout=25.0
        )
        return ChatResponse(
            reply=result.get("reply", ""),
            recommendations=result.get("recommendations", []),
            end_of_conversation=result.get("end_of_conversation", False)
        )
    except asyncio.TimeoutError:
        return ChatResponse(
            reply="I'm taking too long to respond. Please try again.",
            recommendations=[],
            end_of_conversation=False
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))