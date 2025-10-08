from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.tasks import get_current_user  # Import from tasks.py instead
from app.models.user import User, EmployeeProfile
from app.models.task import LeaveRequest, Task, TaskStatus
from app.schemas.task import LeaveRequestCreate, LeaveRequest as LeaveRequestSchema
from app.services.scoring_service import scoring_service
from datetime import datetime

router = APIRouter()

@router.post("/leave-requests", response_model=LeaveRequestSchema)
async def create_leave_request(
    leave_request: LeaveRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new leave request (Employee only)"""
    if current_user.role != "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employees can create leave requests"
        )
    
    # Get employee profile
    employee_profile = db.query(EmployeeProfile).filter(
        EmployeeProfile.user_id == current_user.id
    ).first()
    
    if not employee_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    # Create leave request
    db_leave_request = LeaveRequest(
        employee_id=employee_profile.id,
        start_date=leave_request.start_date,
        end_date=leave_request.end_date,
        reason=leave_request.reason,
        status="pending"
    )
    
    db.add(db_leave_request)
    db.commit()
    db.refresh(db_leave_request)
    
    # Check if employee has active tasks that need transfer
    active_tasks = db.query(Task).filter(
        Task.assigned_to == current_user.id,
        Task.status.in_([TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value])
    ).all()
    
    if active_tasks:
        # Mark that tasks need transfer
        db_leave_request.tasks_transferred = False
    else:
        # No active tasks to transfer
        db_leave_request.tasks_transferred = True
        db_leave_request.transfer_successful = True
    
    db.commit()
    db.refresh(db_leave_request)
    
    return db_leave_request

@router.get("/leave-requests", response_model=List[LeaveRequestSchema])
async def get_leave_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get leave requests (Employee: own requests, Manager: all requests)"""
    if current_user.role == "employee":
        # Get employee's own leave requests
        employee_profile = db.query(EmployeeProfile).filter(
            EmployeeProfile.user_id == current_user.id
        ).first()
        
        if not employee_profile:
            return []
        
        leave_requests = db.query(LeaveRequest).filter(
            LeaveRequest.employee_id == employee_profile.id
        ).all()
    
    elif current_user.role == "manager":
        # Get all leave requests for manager
        leave_requests = db.query(LeaveRequest).all()
    
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return leave_requests

@router.put("/leave-requests/{leave_request_id}/approve")
async def approve_leave_request(
    leave_request_id: int,
    approved: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve or reject a leave request (Manager only)"""
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can approve leave requests"
        )
    
    leave_request = db.query(LeaveRequest).filter(
        LeaveRequest.id == leave_request_id
    ).first()
    
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )
    
    # Update leave request status
    leave_request.status = "approved" if approved else "rejected"
    leave_request.approved_by = current_user.id
    leave_request.approval_date = datetime.utcnow()
    
    # If approved and tasks weren't transferred, update leave score
    if approved and not leave_request.transfer_successful:
        employee_profile = db.query(EmployeeProfile).filter(
            EmployeeProfile.id == leave_request.employee_id
        ).first()
        
        if employee_profile:
            # Update leave score based on task transfer success
            scoring_service.update_leave_score(
                db, 
                employee_profile.user_id, 
                leave_request.transfer_successful
            )
    
    db.commit()
    db.refresh(leave_request)
    
    return {
        "message": f"Leave request {'approved' if approved else 'rejected'}",
        "leave_request": leave_request
    }

@router.post("/leave-requests/{leave_request_id}/transfer-tasks")
async def transfer_tasks_for_leave(
    leave_request_id: int,
    target_employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Transfer tasks for a leave request (Manager only)"""
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can transfer tasks"
        )
    
    leave_request = db.query(LeaveRequest).filter(
        LeaveRequest.id == leave_request_id
    ).first()
    
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )
    
    # Get employee's active tasks
    employee_profile = db.query(EmployeeProfile).filter(
        EmployeeProfile.id == leave_request.employee_id
    ).first()
    
    if not employee_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    active_tasks = db.query(Task).filter(
        Task.assigned_to == employee_profile.user_id,
        Task.status.in_([TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value])
    ).all()
    
    # Transfer tasks to target employee
    transferred_count = 0
    for task in active_tasks:
        task.assigned_to = target_employee_id
        transferred_count += 1
    
    # Update leave request
    leave_request.tasks_transferred = True
    leave_request.transfer_successful = transferred_count > 0
    
    db.commit()
    
    return {
        "message": f"Transferred {transferred_count} tasks successfully",
        "transferred_tasks": transferred_count
    }