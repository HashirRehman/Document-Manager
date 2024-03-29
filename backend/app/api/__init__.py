from fastapi import APIRouter

from .documents import router as documents_router
from .nlp import router as nlp_router

api_router = APIRouter()

api_router.include_router(documents_router, tags=["documents"])
api_router.include_router(nlp_router, tags=["nlp"])
