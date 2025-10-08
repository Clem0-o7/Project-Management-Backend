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