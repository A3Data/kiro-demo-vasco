import sys
sys.path.insert(0, "../agent")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from vasco_agent import create_agent

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

agent = create_agent()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = agent(req.message)
    # Extrair texto da resposta Strands
    if hasattr(result, "message") and isinstance(result.message, dict):
        content = result.message.get("content", [])
        text = "".join(block.get("text", "") for block in content if isinstance(block, dict))
    else:
        text = str(result)
    return ChatResponse(response=text)


@app.get("/health")
def health():
    return {"status": "ok"}
