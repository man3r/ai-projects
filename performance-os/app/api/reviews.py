from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.review import ReviewCycle, Review
from app.schemas.review import ReviewCycleCreate, ReviewCycleResponse, ReviewCreate, ReviewUpdate, ReviewResponse
from app.api.auth import get_current_user_token
from typing import List

router = APIRouter()

@router.post("/cycles", response_model=ReviewCycleResponse)
def create_cycle(
    cycle: ReviewCycleCreate, 
    db: Session = Depends(get_db),
    token_payload: dict = Depends(get_current_user_token)
):
    if token_payload.get("role") not in ["Platform Admin", "Tenant Admin"]:
        raise HTTPException(status_code=403, detail="Only Admins can create review cycles")
        
    new_cycle = ReviewCycle(
        **cycle.model_dump(), 
        organization_id=token_payload.get("organization_id")
    )
    db.add(new_cycle)
    db.commit()
    db.refresh(new_cycle)
    return new_cycle

@router.get("/cycles", response_model=List[ReviewCycleResponse])
def get_cycles(
    db: Session = Depends(get_db),
    token_payload: dict = Depends(get_current_user_token)
):
    tenant_id = token_payload.get("organization_id")
    return db.query(ReviewCycle).filter(ReviewCycle.organization_id == tenant_id).all()

@router.post("/", response_model=ReviewResponse)
def create_review(
    review: ReviewCreate, 
    db: Session = Depends(get_db),
    token_payload: dict = Depends(get_current_user_token)
):
    if token_payload.get("role") not in ["Platform Admin", "Tenant Admin", "Manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to initiate reviews")
        
    new_review = Review(
        **review.model_dump(), 
        organization_id=token_payload.get("organization_id")
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

@router.get("/", response_model=List[ReviewResponse])
def get_reviews(
    cycle_id: int = None,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(get_current_user_token)
):
    tenant_id = token_payload.get("organization_id")
    user_id = token_payload.get("user_id")
    role = token_payload.get("role")
    
    query = db.query(Review).filter(Review.organization_id == tenant_id)
    if cycle_id:
        query = query.filter(Review.cycle_id == cycle_id)
        
    if role == "Employee":
        # Employees only see their own reviews
        query = query.filter(Review.employee_id == user_id)
        
    return query.all()

@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(get_current_user_token)
):
    role = token_payload.get("role")
    user_id = token_payload.get("user_id")
    tenant_id = token_payload.get("organization_id")
    
    db_review = db.query(Review).filter(Review.id == review_id, Review.organization_id == tenant_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
        
    if review_update.self_reflection is not None:
        if db_review.employee_id != user_id:
             raise HTTPException(status_code=403, detail="Only the employee can write their self reflection")
        db_review.self_reflection = review_update.self_reflection
        
    if review_update.manager_assessment is not None or review_update.final_rating is not None:
        if role not in ["Manager", "Tenant Admin", "Platform Admin"]:
             raise HTTPException(status_code=403, detail="Only managers can write assessments and ratings")
        if review_update.manager_assessment is not None:
             db_review.manager_assessment = review_update.manager_assessment
        if review_update.final_rating is not None:
             db_review.final_rating = review_update.final_rating
             
    if review_update.status is not None:
         db_review.status = review_update.status
         
    db.commit()
    db.refresh(db_review)
    return db_review
