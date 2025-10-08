from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import verify_password, get_password_hash, create_access_token
from app.models.user import User, EmployeeProfile, ManagerProfile
from app.schemas.user import UserCreate, User as UserSchema, Token, EmployeeProfile as EmployeeProfileSchema, ManagerProfile as ManagerProfileSchema
from datetime import timedelta
from app.core.config import settings

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        password_hash=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create user
    db_user = create_user(db, user)
    
    # Create profile based on role
    profile = None
    if user.role == "employee":
        profile_data = EmployeeProfile(user_id=db_user.id, name="New Employee")
        db.add(profile_data)
        db.commit()
        db.refresh(profile_data)
        profile = profile_data
    elif user.role == "manager":
        profile_data = ManagerProfile(user_id=db_user.id, name="New Manager")
        db.add(profile_data)
        db.commit()
        db.refresh(profile_data)
        profile = profile_data
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": db_user.email, "role": db_user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user,
        "profile": profile
    }

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user profile
    profile = None
    if user.role == "employee":
        profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == user.id).first()
    elif user.role == "manager":
        profile = db.query(ManagerProfile).filter(ManagerProfile.user_id == user.id).first()
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
        "profile": profile
    }