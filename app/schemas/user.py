from pydantic import BaseModel, EmailStr
from typing import Optional, Union
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: str  # Changed from EmailStr to str for simplicity
    role: str  # 'employee' or 'manager'

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str  # Changed from EmailStr to str
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Employee Profile schemas
class EmployeeProfileBase(BaseModel):
    name: str
    position: Optional[str] = None

class EmployeeProfileCreate(EmployeeProfileBase):
    pass

class EmployeeProfile(EmployeeProfileBase):
    id: int
    user_id: int
    score: int
    leave_score: int
    success_rate: float
    tasks_completed: int
    tasks_failed: int
    
    class Config:
        from_attributes = True

# Manager Profile schemas
class ManagerProfileBase(BaseModel):
    name: str
    salary: Optional[float] = 100000.0
    team_size: Optional[int] = 10

class ManagerProfileCreate(ManagerProfileBase):
    pass

class ManagerProfile(ManagerProfileBase):
    id: int
    user_id: int
    projects_count: int
    success_rate: float
    
    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: User
    profile: Optional[Union[EmployeeProfile, ManagerProfile]] = None

class TokenData(BaseModel):
    email: Optional[str] = None