from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # The crucial multi-tenant requirement: every user belongs to an organization
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Career levels and roles
    job_title = Column(String, nullable=True)
    department = Column(String, nullable=True)
    role = Column(String, default="employee") # employee, manager, admin
    
    # Manager relationship (self-referential)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization")
    manager = relationship("User", remote_side=[id], backref="direct_reports")
