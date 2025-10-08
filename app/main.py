from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base

# Import models to ensure they are registered with SQLAlchemy
from app.models.user import User, EmployeeProfile, ManagerProfile
from app.models.task import Task, TaskStatusReport, LeaveRequest

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Powered Project Management System",
    description="Backend API for project management with AI features",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else settings.allowed_hosts,  # Configure for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "AI-Powered Project Management System API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include API routers
from app.api import auth, tasks, analytics, leave

app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(leave.router, prefix="/api/leave", tags=["leave"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)