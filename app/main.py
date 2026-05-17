from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from app.api.chat import router as chat_router


app = FastAPI(
    title="SHL Assessment Recommendation API"
)


@app.get("/health")
def health():

    return {
        "status": "ok"
    }


app.include_router(chat_router)