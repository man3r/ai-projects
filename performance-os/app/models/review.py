from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class ReviewCycle(Base):
    __tablename__ = "review_cycles"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String, nullable=False) # e.g., "H1 2026 Review"
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="draft") # draft, active, closed
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Review(Base):
    """
    Individual performance review for a user in a given cycle.
    """
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    cycle_id = Column(Integer, ForeignKey("review_cycles.id"), nullable=False)
    
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Manager at the time of review
    
    self_reflection = Column(Text, nullable=True)
    manager_assessment = Column(Text, nullable=True)
    final_rating = Column(Float, nullable=True) # E.g., 1.0 to 5.0
    status = Column(String, default="self_reflection_pending") # self_reflection_pending, manager_review_pending, calibrated, finished
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    cycle = relationship("ReviewCycle")
    employee = relationship("User", foreign_keys=[employee_id])
    manager = relationship("User", foreign_keys=[manager_id])
