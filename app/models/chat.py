from pydantic import BaseModel
from typing import List


class Message(BaseModel):

    role: str

    content: str


class ChatRequest(BaseModel):

    messages: List[Message]


class Recommendation(BaseModel):

    name: str

    url: str

    reason: str

    categories: list


class ChatResponse(BaseModel):

    reply: str

    recommendations: list

    end_of_conversation: bool