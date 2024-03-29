from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field

from ..services import NLPService

class Question(BaseModel):
    question: str = Field(min_length=5, max_length=255)

router = APIRouter()

@router.post("/nlp/search", response_model=str)
async def search(
    question: Question,
    nlp_service: NLPService = Depends()
) -> str:
    """
    Perform a question-answering task using the RAG Agent powered by NLP.
    """

    try:
        answer = await nlp_service.search_and_get_answer(question.question)
        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during NLP processing: {str(e)}")

@router.post("/nlp/sentiment", response_model=str)
async def analyze_sentiment(question: str) -> str:
    """Analyze the sentiment of the given question."""

@router.post("/nlp/entities", response_model=List[str])
async def extract_entities(question: str) -> List[str]:
    """Extract entities from the given question."""
