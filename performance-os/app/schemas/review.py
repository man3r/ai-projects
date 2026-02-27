from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# Review Cycle Schemas
class ReviewCycleBase(BaseModel):
    name: str # e.g., "H1 2026 Review"
    start_date: datetime
    end_date: datetime
    status: Optional[str] = "draft" # draft, active, closed

class ReviewCycleCreate(ReviewCycleBase):
    pass

class ReviewCycleResponse(ReviewCycleBase):
    id: int
    organization_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Individual Review Schemas
class ReviewBase(BaseModel):
    employee_id: int
    manager_id: Optional[int] = None
    
class ReviewCreate(ReviewBase):
    cycle_id: int

class ReviewUpdate(BaseModel):
    self_reflection: Optional[str] = None
    manager_assessment: Optional[str] = None
    final_rating: Optional[float] = None
    status: Optional[str] = None # self_reflection_pending, manager_review_pending, calibrated, finished

class ReviewResponse(ReviewBase):
    id: int
    organization_id: int
    cycle_id: int
    self_reflection: Optional[str] = None
    manager_assessment: Optional[str] = None
    final_rating: Optional[float] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
