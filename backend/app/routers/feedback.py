"""
routers/feedback.py — POST /api/feedback
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.db import Message
from app.models.schemas import FeedbackRequest, FeedbackResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse, summary="Submit thumbs up/down on a response")
async def submit_feedback(
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
) -> FeedbackResponse:
    """
    Record a user thumbs-up (1) or thumbs-down (-1) rating on an assistant message.
    """
    if request.rating not in {1, -1}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="rating must be 1 (thumbs up) or -1 (thumbs down).",
        )

    message: Message | None = await db.get(Message, request.message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message '{request.message_id}' not found.",
        )

    message.rating = request.rating
    logger.info(
        f"Feedback recorded: message={request.message_id} rating={request.rating}"
    )

    return FeedbackResponse(ok=True, message_id=request.message_id)
