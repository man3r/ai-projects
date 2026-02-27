from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class GoalFrameworkBase(BaseModel):
    name: str
    tier1_name: Optional[str] = "Focus Area"
    tier2_name: Optional[str] = "Objective"
    tier3_name: Optional[str] = "Measure"

class GoalFrameworkCreate(GoalFrameworkBase):
    organization_id: int

class GoalFrameworkResponse(GoalFrameworkBase):
    id: int
    organization_id: int
    
    model_config = ConfigDict(from_attributes=True)

class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    tier_level: int
    target_value: Optional[float] = None
    current_value: Optional[float] = 0.0
    unit: Optional[str] = None
    weightage: Optional[float] = None

class GoalCreate(GoalBase):
    framework_id: int
    parent_goal_id: Optional[int] = None
    owner_id: Optional[int] = None

class GoalResponse(GoalBase):
    id: int
    organization_id: int
    framework_id: int
    parent_goal_id: Optional[int] = None
    owner_id: Optional[int] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
