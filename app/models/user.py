from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # 'employee' or 'manager'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee_profile = relationship("EmployeeProfile", back_populates="user", uselist=False)
    manager_profile = relationship("ManagerProfile", back_populates="user", uselist=False)
    assigned_tasks = relationship("Task", foreign_keys="Task.assigned_to", back_populates="assignee")
    created_tasks = relationship("Task", foreign_keys="Task.created_by", back_populates="creator")

class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    name = Column(String(255), nullable=False)
    position = Column(String(255))
    score = Column(Integer, default=0)
    leave_score = Column(Integer, default=100)
    success_rate = Column(Float, default=0.0)
    tasks_completed = Column(Integer, default=0)
    tasks_failed = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="employee_profile")
    leave_requests = relationship("LeaveRequest", back_populates="employee")

class ManagerProfile(Base):
    __tablename__ = "manager_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    name = Column(String(255), nullable=False)
    salary = Column(Float, default=100000.0)
    projects_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    team_size = Column(Integer, default=10)
    
    # Relationships
    user = relationship("User", back_populates="manager_profile")