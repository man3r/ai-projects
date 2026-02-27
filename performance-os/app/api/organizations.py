from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.tenant import Organization
from app.schemas.tenant import OrganizationCreate, OrganizationResponse
from app.api.auth import get_current_user_token
from typing import List

router = APIRouter()

@router.post("/", response_model=OrganizationResponse)
def create_organization(org: OrganizationCreate, db: Session = Depends(get_db)):
    db_org = db.query(Organization).filter(Organization.slug == org.slug).first()
    if db_org:
        raise HTTPException(status_code=400, detail="Organization slug already registered")
    
    new_org = Organization(name=org.name, slug=org.slug, is_active=org.is_active)
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    return new_org

@router.get("/", response_model=List[OrganizationResponse])
def get_organizations(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    token_payload: dict = Depends(get_current_user_token)
):
    role = token_payload.get("role")
    tenant_id = token_payload.get("organization_id")
    
    if role == "Platform Admin":
        orgs = db.query(Organization).offset(skip).limit(limit).all()
    else:
        orgs = db.query(Organization).filter(Organization.id == tenant_id).offset(skip).limit(limit).all()
        
    return orgs

@router.get("/{org_id}", response_model=OrganizationResponse)
def get_organization(
    org_id: int, 
    db: Session = Depends(get_db),
    token_payload: dict = Depends(get_current_user_token)
):
    role = token_payload.get("role")
    tenant_id = token_payload.get("organization_id")
    
    if role != "Platform Admin" and tenant_id != org_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this organization")
        
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org
