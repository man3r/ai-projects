from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.auth import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from typing import List
from jose import JWTError, jwt
from app.auth import SECRET_KEY, ALGORITHM

# This defines the token URL that Swagger UI and dependencies will use
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        job_title=user.job_title,
        department=user.department,
        role=user.role,
        organization_id=user.organization_id,
        manager_id=user.manager_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Standard OAuth2 compatible token login, getting username and password from form data.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Payload includes vital multi-tenant data so downstream routers don't need to query db again
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "organization_id": user.organization_id,
            "role": user.role
        }, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}




def get_current_user_token(token: str = Depends(oauth2_scheme)):
    """
    Dependency to validate the JWT in API routes and extract the multi-tenant info.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        org_id: int = payload.get("organization_id")
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        if email is None or org_id is None:
            raise credentials_exception
            
        return payload
    except JWTError:
        raise credentials_exception

@router.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), token_payload: dict = Depends(get_current_user_token)):
    tenant_id = token_payload.get("organization_id")
    users = db.query(User).filter(User.organization_id == tenant_id).all()
    return users
