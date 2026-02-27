from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class FeedbackBase(BaseModel):
    receiver_id: int
    feedback_type: str # "kudo", "constructive"
    message: str
    is_public: Optional[bool] = True

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackResponse(FeedbackBase):
    id: int
    organization_id: int
    sender_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
