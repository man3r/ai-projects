from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class OrganizationBase(BaseModel):
    name: str
    slug: str
    is_active: Optional[bool] = True

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
