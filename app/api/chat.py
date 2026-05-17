from fastapi import APIRouter

from app.models.chat import (
    ChatRequest,
    ChatResponse
)

from app.services.chat_orchestrator import (
    ChatOrchestrator
)

from app.core.services import (
    recommendation_engine
)


router = APIRouter()

orchestrator = ChatOrchestrator(
    recommendation_engine
)


@router.post(
    "/chat",
    response_model=ChatResponse
)
def chat(request: ChatRequest, session_id: str = "default"):

    try:

        response = orchestrator.handle_chat(
            [message.dict() for message in request.messages],
            session_id=session_id
        )

        return ChatResponse(
            reply=response["reply"],
            recommendations=response["recommendations"],
            end_of_conversation=response[
                "end_of_conversation"
            ]
        )

    except Exception as e:

        print(f"Chat API Error: {str(e)}")

        return ChatResponse(
            reply=(
                "An internal error occurred while "
                "processing the request."
            ),
            recommendations=[],
            end_of_conversation=False
        )