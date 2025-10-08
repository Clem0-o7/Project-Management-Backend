from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TRANSFERRED = "transferred"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Task schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    score_value: int = 1000
    estimated_hours: Optional[float] = None
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    assigned_to: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    actual_hours: Optional[float] = None
    progress_percentage: Optional[int] = None

class Task(TaskBase):
    id: int
    assigned_to: Optional[int]
    created_by: int
    status: TaskStatus
    risk_factor: float
    actual_hours: Optional[float]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    # AI fields
    ai_difficulty_assessment: Optional[str]
    ai_risk_factors: Optional[str]
    ai_recommendations: Optional[str]
    
    class Config:
        from_attributes = True

# Task Status Report schemas
class TaskStatusReportBase(BaseModel):
    report_text: str
    progress_percentage: int = 0

class TaskStatusReportCreate(TaskStatusReportBase):
    task_id: int

class TaskStatusReport(TaskStatusReportBase):
    id: int
    task_id: int
    employee_id: int
    ai_feedback: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Leave Request schemas
class LeaveRequestBase(BaseModel):
    start_date: datetime
    end_date: datetime
    reason: str

class LeaveRequestCreate(LeaveRequestBase):
    pass

class LeaveRequest(LeaveRequestBase):
    id: int
    employee_id: int
    status: str
    approved_by: Optional[int]
    approval_date: Optional[datetime]
    tasks_transferred: bool
    transfer_successful: bool
    created_at: datetime
    
    class Config:
        from_attributes = True