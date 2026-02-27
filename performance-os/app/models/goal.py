from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class GoalFramework(Base):
    """
    Defines the structural terminology for an organization's goals.
    E.g. "Focus Area", "Objective", "Measure"
    """
    __tablename__ = "goal_frameworks"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String, nullable=False) # E.g., "Food Safety PMS" or "Standard OKRs"
    
    # Defines the terminology used at 3 tiers
    tier1_name = Column(String) # e.g. "Focus Area"
    tier2_name = Column(String) # e.g. "Objective"
    tier3_name = Column(String) # e.g. "Measure (KPI)"

class Goal(Base):
    """
    A unified Goal model that can adapt to the Framework.
    """
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    framework_id = Column(Integer, ForeignKey("goal_frameworks.id"), nullable=False)
    
    # Ownership
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Goal metadata
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # For hierarchical goals (Objectives belonging to Focus Areas)
    parent_goal_id = Column(Integer, ForeignKey("goals.id"), nullable=True)
    
    tier_level = Column(Integer, nullable=False) # 1, 2, or 3 based on framework
    
    # For measurable goals (Tier 3)
    target_value = Column(Float, nullable=True)
    current_value = Column(Float, default=0.0)
    unit = Column(String, nullable=True) # e.g. "%", "days"
    weightage = Column(Float, nullable=True) # E.g. 0.20 for 20%
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("User")
    parent_goal = relationship("Goal", remote_side=[id], backref="child_goals")
