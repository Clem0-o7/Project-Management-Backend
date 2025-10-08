from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
from enum import Enum as PyEnum

# Import here to avoid circular imports - we'll use string references for relationships

class TaskStatus(PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TRANSFERRED = "transferred"

class TaskPriority(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    status = Column(String(50), default=TaskStatus.PENDING.value)
    priority = Column(String(50), default=TaskPriority.MEDIUM.value)
    score_value = Column(Integer, default=1000)
    risk_factor = Column(Float, default=0.0)
    estimated_hours = Column(Float)
    actual_hours = Column(Float)
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # AI-generated fields
    ai_difficulty_assessment = Column(Text)
    ai_risk_factors = Column(Text)
    ai_recommendations = Column(Text)
    
    # Relationships
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tasks")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_tasks")
    status_reports = relationship("TaskStatusReport", back_populates="task")

class TaskStatusReport(Base):
    __tablename__ = "task_status_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    employee_id = Column(Integer, ForeignKey("users.id"))
    report_text = Column(Text)
    progress_percentage = Column(Integer, default=0)
    ai_feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="status_reports")
    employee = relationship("User")

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employee_profiles.id"))  # Fixed: should reference employee_profiles.id
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    reason = Column(Text)
    status = Column(String(50), default="pending")  # pending, approved, rejected
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approval_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Task transfer tracking
    tasks_transferred = Column(Boolean, default=False)
    transfer_successful = Column(Boolean, default=False)
    
    # Relationships
    employee = relationship("EmployeeProfile", back_populates="leave_requests")
    approver = relationship("User", foreign_keys=[approved_by])