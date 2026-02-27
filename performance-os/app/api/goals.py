from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.goal import GoalFramework, Goal
from app.models.tenant import Organization
from app.schemas.goal import GoalCreate, GoalResponse, GoalFrameworkCreate, GoalFrameworkResponse
from app.api.auth import get_current_user_token
from typing import List

router = APIRouter()

@router.post("/frameworks", response_model=GoalFrameworkResponse)
def create_framework(
    framework: GoalFrameworkCreate, 
    db: Session = Depends(get_db),
    token_payload: dict = Depends(get_current_user_token)
):
    tenant_id = token_payload.get("organization_id")
    role = token_payload.get("role")
    
    if role not in ["Platform Admin", "Tenant Admin"]:
        raise HTTPException(status_code=403, detail="Only Tenant Admins can create frameworks")
        
    # Verify tenant
    if framework.organization_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    # Check if org exists
    org = db.query(Organization).filter(Organization.id == tenant_id).first()
    if not org:
         raise HTTPException(status_code=404, detail="Organization not found")

    new_fw = GoalFramework(**framework.model_dump())
    db.add(new_fw)
    db.commit()
    db.refresh(new_fw)
    return new_fw

@router.get("/frameworks", response_model=List[GoalFrameworkResponse])
def get_frameworks(
    db: Session = Depends(get_db),
    token_payload: dict = Depends(get_current_user_token)
):
    tenant_id = token_payload.get("organization_id")
    return db.query(GoalFramework).filter(GoalFramework.organization_id == tenant_id).all()

@router.post("/", response_model=GoalResponse)
def create_goal(
    goal: GoalCreate, 
    db: Session = Depends(get_db),
    token_payload: dict = Depends(get_current_user_token)
):
    tenant_id = token_payload.get("organization_id")
    # Multi-tenant scoping logic: ensure the framework belongs to this tenant
    fw = db.query(GoalFramework).filter(GoalFramework.id == goal.framework_id, GoalFramework.organization_id == tenant_id).first()
    if not fw:
        raise HTTPException(status_code=404, detail="Goal Framework not found for this organization")

    new_goal = Goal(**goal.model_dump(), organization_id=tenant_id)
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return new_goal

@router.get("/", response_model=List[GoalResponse])
def get_goals(
    db: Session = Depends(get_db),
    token_payload: dict = Depends(get_current_user_token)
):
    tenant_id = token_payload.get("organization_id")
    return db.query(Goal).filter(Goal.organization_id == tenant_id).all()
