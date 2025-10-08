from sqlalchemy.orm import Session
from app.models.user import User, EmployeeProfile
from app.models.task import Task, TaskStatus
from typing import List, Dict

class ScoringService:
    
    def calculate_employee_score(self, db: Session, employee_id: int) -> int:
        """Calculate total score for an employee"""
        employee = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == employee_id).first()
        if not employee:
            return 0
        
        # Get completed tasks
        completed_tasks = db.query(Task).filter(
            Task.assigned_to == employee_id,
            Task.status == TaskStatus.COMPLETED.value
        ).all()
        
        # Get failed tasks
        failed_tasks = db.query(Task).filter(
            Task.assigned_to == employee_id,
            Task.status == TaskStatus.FAILED.value
        ).all()
        
        # Calculate score: +1000 for completed, -2000 for failed
        score = sum(task.score_value for task in completed_tasks)
        score -= sum(task.score_value * 2 for task in failed_tasks)
        
        # Update employee profile
        employee.score = max(0, score)  # Don't allow negative scores
        employee.tasks_completed = len(completed_tasks)
        employee.tasks_failed = len(failed_tasks)
        
        # Calculate success rate
        total_tasks = len(completed_tasks) + len(failed_tasks)
        if total_tasks > 0:
            employee.success_rate = (len(completed_tasks) / total_tasks) * 100
        else:
            employee.success_rate = 0.0
        
        db.commit()
        return employee.score
    
    def get_leaderboard(self, db: Session, limit: int = 10) -> List[Dict]:
        """Get employee leaderboard"""
        employees = db.query(EmployeeProfile).order_by(EmployeeProfile.score.desc()).limit(limit).all()
        
        leaderboard = []
        for i, emp in enumerate(employees, 1):
            leaderboard.append({
                "rank": i,
                "name": emp.name,
                "position": emp.position,
                "score": emp.score,
                "success_rate": emp.success_rate,
                "tasks_completed": emp.tasks_completed,
                "leave_score": emp.leave_score
            })
        
        return leaderboard
    
    def update_leave_score(self, db: Session, employee_id: int, task_transferred: bool) -> int:
        """Update leave score based on task transfer success"""
        employee = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == employee_id).first()
        if not employee:
            return 0
        
        if not task_transferred:
            # Reduce leave score if tasks couldn't be transferred
            penalty = 10  # Configurable penalty
            employee.leave_score = max(0, employee.leave_score - penalty)
        
        db.commit()
        return employee.leave_score
    
    def calculate_team_stats(self, db: Session) -> Dict:
        """Calculate overall team statistics"""
        from sqlalchemy import func
        
        total_employees = db.query(EmployeeProfile).count()
        
        if total_employees == 0:
            return {
                "total_employees": 0,
                "average_score": 0,
                "average_success_rate": 0,
                "total_tasks_completed": 0,
                "total_tasks_pending": 0
            }
        
        # Average score
        avg_score = db.query(func.avg(EmployeeProfile.score)).scalar() or 0
        
        # Average success rate
        avg_success_rate = db.query(func.avg(EmployeeProfile.success_rate)).scalar() or 0
        
        # Total tasks
        total_completed = db.query(Task).filter(Task.status == TaskStatus.COMPLETED.value).count()
        total_pending = db.query(Task).filter(Task.status.in_([
            TaskStatus.PENDING.value,
            TaskStatus.IN_PROGRESS.value
        ])).count()
        
        return {
            "total_employees": total_employees,
            "average_score": round(float(avg_score), 2),
            "average_success_rate": round(float(avg_success_rate), 2),
            "total_tasks_completed": total_completed,
            "total_tasks_pending": total_pending
        }

# Global scoring service instance
scoring_service = ScoringService()