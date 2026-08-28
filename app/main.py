from fastapi import FastAPI

from app.api.routes.sessions import router as sessions_router


app = FastAPI(
    title="OpenAI Chat Service"
)


app.include_router(sessions_router)


@app.get("/")
def root():
    return {
        "message": "OpenAI Chat Service is running"
    }