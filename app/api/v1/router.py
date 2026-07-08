from fastapi import APIRouter
from app.api.v1 import research

api_router = APIRouter()
api_router.include_router(research.router)