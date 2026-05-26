from fastapi import APIRouter
from backend.app.api.endpoints import hypnosis, history

api_router = APIRouter()

api_router.include_router(hypnosis.router, tags=["Hypnosis Generation"])
api_router.include_router(history.router, tags=["Dashboard & History"])
