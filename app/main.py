from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Multi-Agent Banking Support",
    description="AI-powered customer support system with multi-agent orchestration",
    version="0.1.0",
)

app.include_router(router, tags=["chat"])
