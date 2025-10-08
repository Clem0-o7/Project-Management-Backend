from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.models.task import Task, TaskStatusReport
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, Task as TaskSchema, TaskStatusReportCreate, TaskStatusReport as TaskStatusReportSchema
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=TaskSchema)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new task (Manager only)"""
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can create tasks"
        )
    
    db_task = Task(
        title=task.title,
        description=task.description,
        assigned_to=task.assigned_to,
        created_by=current_user.id,
        priority=task.priority.value,
        score_value=task.score_value,
        estimated_hours=task.estimated_hours,
        due_date=task.due_date
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/", response_model=List[TaskSchema])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get tasks based on user role"""
    if current_user.role == "employee":
        # Employees see only their assigned tasks
        tasks = db.query(Task).filter(Task.assigned_to == current_user.id).offset(skip).limit(limit).all()
    else:
        # Managers see all tasks
        tasks = db.query(Task).offset(skip).limit(limit).all()
    return tasks

@router.get("/{task_id}", response_model=TaskSchema)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check permissions
    if current_user.role == "employee" and task.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own tasks"
        )
    
    return task

@router.put("/{task_id}", response_model=TaskSchema)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check permissions
    if current_user.role == "employee" and task.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own tasks"
        )
    
    # Update fields
    for field, value in task_update.dict(exclude_unset=True).items():
        if hasattr(task, field):
            setattr(task, field, value.value if hasattr(value, 'value') else value)
    
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a task (Manager only)"""
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can delete tasks"
        )
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}

@router.post("/{task_id}/reports", response_model=TaskStatusReportSchema)
async def create_status_report(
    task_id: int,
    report: TaskStatusReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a status report for a task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if current_user.role == "employee" and task.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only report on your own tasks"
        )
    
    db_report = TaskStatusReport(
        task_id=task_id,
        employee_id=current_user.id,
        report_text=report.report_text,
        progress_percentage=report.progress_percentage
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

@router.post("/{task_id}/status")
async def update_task_status(
    task_id: int,
    status_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update task status"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check permissions
    if current_user.role == "employee" and task.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own tasks"
        )
    
    # Update status
    new_status = status_data.get("status")
    if new_status:
        task.status = new_status
        
        # Update completion date if completed
        if new_status == "completed":
            task.completed_at = datetime.now()
    
    db.commit()
    db.refresh(task)
    return {"message": "Task status updated successfully", "task": task}

@router.post("/ai/chat")
async def ai_chat(
    chat_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI Chat functionality"""
    message = chat_data.get("message", "")
    
    # Simple AI response for now - you can integrate with actual AI later
    if "task" in message.lower():
        response = "I can help you with task management! You can create, update, or check the status of tasks. What would you like to do?"
    elif "deadline" in message.lower() or "due" in message.lower():
        response = "I can help you track deadlines. Would you like me to show you upcoming deadlines or help extend a deadline?"
    elif "progress" in message.lower():
        response = "I can help you track progress on your tasks. Would you like to see your progress overview?"
    elif "team" in message.lower():
        if current_user.role == "manager":
            response = "I can help you manage your team! You can view team performance, assign tasks, or check team statistics."
        else:
            response = "I can help you coordinate with your team. You can check team updates or communicate progress."
    else:
        response = "Hello! I'm your AI assistant. I can help you with task management, deadlines, progress tracking, and team coordination. What can I help you with today?"
    
    return {
        "response": response,
        "timestamp": "2024-01-01T00:00:00Z"  # You can use actual timestamp
    }

@router.get("/{task_id}/reports", response_model=List[TaskStatusReportSchema])
async def get_task_reports(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all status reports for a task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check permissions
    if current_user.role == "employee" and task.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view reports for your own tasks"
        )
    
    reports = db.query(TaskStatusReport).filter(TaskStatusReport.task_id == task_id).all()
    return reports