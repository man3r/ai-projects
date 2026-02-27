from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.api.auth import get_current_user_token
from typing import List

router = APIRouter()

@router.post("/", response_model=FeedbackResponse)
def create_feedback(
    feedback: FeedbackCreate, 
    db: Session = Depends(get_db),
    token_payload: dict = Depends(get_current_user_token)
):
    new_fb = Feedback(
        **feedback.model_dump(),
        organization_id=token_payload.get("organization_id"),
        sender_id=token_payload.get("user_id")
    )
    db.add(new_fb)
    db.commit()
    db.refresh(new_fb)
    return new_fb

@router.get("/", response_model=List[FeedbackResponse])
def get_feedbacks(
    receiver_id: int = None,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(get_current_user_token)
):
    tenant_id = token_payload.get("organization_id")
    query = db.query(Feedback).filter(Feedback.organization_id == tenant_id)
    
    if receiver_id:
        query = query.filter(Feedback.receiver_id == receiver_id)
        
    # By default, only show public feedback unless the user is the receiver or sender
    # Note: Complex read permissions can be added here
    
    return query.all()
