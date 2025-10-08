from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.services.scoring_service import scoring_service

router = APIRouter()

@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get employee leaderboard (Manager only)"""
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can view the leaderboard"
        )
    
    leaderboard = scoring_service.get_leaderboard(db, limit)
    return {"leaderboard": leaderboard}

@router.get("/team-stats")
async def get_team_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get team statistics (Manager only)"""
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can view team statistics"
        )
    
    stats = scoring_service.calculate_team_stats(db)
    return stats

@router.post("/recalculate-scores")
async def recalculate_scores(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Recalculate all employee scores (Manager only)"""
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can recalculate scores"
        )
    
    # Get all employees
    employees = db.query(User).filter(User.role == "employee").all()
    updated_scores = {}
    
    for employee in employees:
        new_score = scoring_service.calculate_employee_score(db, employee.id)
        updated_scores[employee.email] = new_score
    
    return {
        "message": f"Recalculated scores for {len(employees)} employees",
        "updated_scores": updated_scores
    }

@router.get("/dashboard")
async def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard analytics data"""
    from app.models.task import Task
    from sqlalchemy import func
    
    if current_user.role == "manager":
        # Manager dashboard - all tasks
        total_tasks = db.query(Task).count()
        completed_tasks = db.query(Task).filter(Task.status == "completed").count()
        in_progress_tasks = db.query(Task).filter(Task.status == "in_progress").count()
        pending_tasks = db.query(Task).filter(Task.status == "pending").count()
        overdue_tasks = db.query(Task).filter(
            Task.status != "completed",
            Task.due_date < func.now()
        ).count()
        
        # Team stats
        team_stats = scoring_service.calculate_team_stats(db)
        
        return {
            "totalTasks": total_tasks,
            "completedTasks": completed_tasks,
            "inProgressTasks": in_progress_tasks,
            "pendingTasks": pending_tasks,
            "overdueTasks": overdue_tasks,
            "teamStats": team_stats
        }
    else:
        # Employee dashboard - only their tasks
        total_tasks = db.query(Task).filter(Task.assigned_to == current_user.id).count()
        completed_tasks = db.query(Task).filter(
            Task.assigned_to == current_user.id,
            Task.status == "completed"
        ).count()
        in_progress_tasks = db.query(Task).filter(
            Task.assigned_to == current_user.id,
            Task.status == "in_progress"
        ).count()
        pending_tasks = db.query(Task).filter(
            Task.assigned_to == current_user.id,
            Task.status == "pending"
        ).count()
        overdue_tasks = db.query(Task).filter(
            Task.assigned_to == current_user.id,
            Task.status != "completed",
            Task.due_date < func.now()
        ).count()
        
        return {
            "totalTasks": total_tasks,
            "completedTasks": completed_tasks,
            "inProgressTasks": in_progress_tasks,
            "pendingTasks": pending_tasks,
            "overdueTasks": overdue_tasks
        }

@router.get("/user-performance")
async def get_user_performance(
    user_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user performance metrics"""
    from app.models.task import Task
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # Determine which user's performance to get
    target_user_id = user_id if user_id and current_user.role == "manager" else current_user.id
    
    # Get tasks for the user
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    recent_tasks = db.query(Task).filter(
        Task.assigned_to == target_user_id,
        Task.created_at >= thirty_days_ago
    ).all()
    
    total_tasks = len(recent_tasks)
    completed_tasks = len([t for t in recent_tasks if t.status == "completed"])
    overdue_tasks = len([t for t in recent_tasks if t.status != "completed" and t.due_date < datetime.now()])
    
    # Calculate performance metrics
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    avg_completion_time = 0  # You could calculate this based on task creation and completion dates
    
    # Get user profile
    user = db.query(User).filter(User.id == target_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile = user.employee_profile if user.role == "employee" else user.manager_profile
    
    return {
        "userId": target_user_id,
        "name": profile.name if profile else user.email,
        "totalTasks": total_tasks,
        "completedTasks": completed_tasks,
        "overdueTasks": overdue_tasks,
        "completionRate": completion_rate,
        "averageCompletionTime": avg_completion_time,
        "score": profile.score if hasattr(profile, 'score') else 0
    }

@router.get("/my-stats")
async def get_my_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's statistics"""
    if current_user.role == "employee":
        # Recalculate and return employee stats
        scoring_service.calculate_employee_score(db, current_user.id)
        
        profile = current_user.employee_profile
        if not profile:
            raise HTTPException(status_code=404, detail="Employee profile not found")
        
        return {
            "name": profile.name,
            "position": profile.position,
            "score": profile.score,
            "leave_score": profile.leave_score,
            "success_rate": profile.success_rate,
            "tasks_completed": profile.tasks_completed,
            "tasks_failed": profile.tasks_failed
        }
    
    elif current_user.role == "manager":
        profile = current_user.manager_profile
        if not profile:
            raise HTTPException(status_code=404, detail="Manager profile not found")
        
        team_stats = scoring_service.calculate_team_stats(db)
        
        return {
            "name": profile.name,
            "salary": profile.salary,
            "projects_count": profile.projects_count,
            "success_rate": profile.success_rate,
            "team_size": profile.team_size,
            "team_stats": team_stats
        }