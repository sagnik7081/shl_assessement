from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@router.post("/chat")
def chat(request: ChatRequest):

    return {
        "reply": "System initialized.",
        "recommendations": [],
        "end_of_conversation": False
    }