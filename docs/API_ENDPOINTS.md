# 📚 API Endpoints Documentation

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-app-name.herokuapp.com`

## Interactive Documentation
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json`

---

## 🔐 Authentication Endpoints

### POST `/api/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "employee" | "manager"
}
```

**Response (201):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "employee",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### POST `/api/auth/login`
Authenticate user and get access token.

**Request Body (Form Data):**
```
username: string
password: string
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "employee"
  }
}
```

### GET `/api/auth/me`
Get current user information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "employee",
  "is_active": true,
  "profile": {
    "full_name": "John Doe",
    "department": "Engineering",
    "phone": "+1234567890"
  }
}
```

---

## 📋 Task Management Endpoints

### GET `/api/tasks/`
Get all tasks (filtered by user role).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status`: Filter by task status (optional)
- `priority`: Filter by priority (optional)
- `assigned_to`: Filter by assigned user ID (optional)

**Response (200):**
```json
[
  {
    "id": 1,
    "title": "Implement user authentication",
    "description": "Add JWT-based authentication system",
    "status": "in_progress",
    "priority": "high",
    "created_by": 2,
    "assigned_to": 1,
    "due_date": "2024-01-15T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-05T00:00:00Z"
  }
]
```

### POST `/api/tasks/`
Create a new task (managers only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "priority": "low" | "medium" | "high",
  "assigned_to": 1,
  "due_date": "2024-01-15T00:00:00Z"
}
```

**Response (201):**
```json
{
  "id": 1,
  "title": "Implement user authentication",
  "description": "Add JWT-based authentication system",
  "status": "pending",
  "priority": "high",
  "created_by": 2,
  "assigned_to": 1,
  "due_date": "2024-01-15T00:00:00Z",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### GET `/api/tasks/{task_id}`
Get specific task details.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": 1,
  "title": "Implement user authentication",
  "description": "Add JWT-based authentication system",
  "status": "in_progress",
  "priority": "high",
  "created_by": 2,
  "assigned_to": 1,
  "due_date": "2024-01-15T00:00:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-05T00:00:00Z",
  "status_reports": [
    {
      "id": 1,
      "status": "in_progress",
      "notes": "Authentication middleware implemented",
      "created_at": "2024-01-05T00:00:00Z"
    }
  ]
}
```

### PUT `/api/tasks/{task_id}`
Update task details (managers only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "status": "pending" | "in_progress" | "completed" | "cancelled",
  "priority": "low" | "medium" | "high",
  "assigned_to": 1,
  "due_date": "2024-01-15T00:00:00Z"
}
```

### DELETE `/api/tasks/{task_id}`
Delete a task (managers only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204):** No content

### POST `/api/tasks/{task_id}/status`
Update task status (assigned user or manager).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "status": "pending" | "in_progress" | "completed" | "cancelled",
  "notes": "Optional status update notes"
}
```

**Response (200):**
```json
{
  "id": 1,
  "task_id": 1,
  "status": "completed",
  "notes": "Task completed successfully",
  "created_at": "2024-01-10T00:00:00Z"
}
```

---

## 🤖 AI-Powered Features

### POST `/api/tasks/ai/assign`
Get AI-powered task assignment recommendations.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "task_title": "Implement user authentication",
  "task_description": "Add JWT-based authentication system",
  "priority": "high",
  "due_date": "2024-01-15",
  "required_skills": ["Python", "FastAPI", "JWT"]
}
```

**Response (200):**
```json
{
  "recommendations": [
    {
      "user_id": 1,
      "username": "john_doe",
      "match_score": 95,
      "reasoning": "Strong experience with Python and FastAPI, has worked on authentication systems before"
    }
  ],
  "success_probability": 0.92,
  "estimated_completion_time": "3-5 days"
}
```

### POST `/api/tasks/ai/risk-assessment`
Get AI risk assessment for a task.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "task_title": "Database migration",
  "task_description": "Migrate from SQLite to PostgreSQL",
  "assigned_to": 1,
  "due_date": "2024-01-20",
  "complexity": "high"
}
```

**Response (200):**
```json
{
  "risk_score": 0.75,
  "risk_level": "medium",
  "risk_factors": [
    "Tight deadline for complex migration",
    "Database migration requires careful planning"
  ],
  "mitigation_strategies": [
    "Create comprehensive backup before migration",
    "Test migration in staging environment first"
  ]
}
```

### POST `/api/tasks/ai/status-feedback`
Get AI feedback on task progress.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "task_id": 1,
  "current_status": "in_progress",
  "progress_notes": "Authentication middleware implemented, working on JWT token generation",
  "time_spent": 8,
  "blockers": ["Need clarification on token expiration policy"]
}
```

**Response (200):**
```json
{
  "feedback": "Good progress on authentication implementation. Recommend setting 30-minute token expiration for security.",
  "suggestions": [
    "Document the authentication flow",
    "Add unit tests for JWT functions"
  ],
  "estimated_completion": "1-2 days",
  "risk_level": "low"
}
```

### POST `/api/tasks/ai/chat`
Chat with AI assistant for work-related queries.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "message": "How should I implement error handling in FastAPI?",
  "context": "Working on API endpoints for task management"
}
```

**Response (200):**
```json
{
  "response": "For FastAPI error handling, use HTTPException for API errors and create custom exception handlers. Here's a recommended approach...",
  "helpful": true,
  "work_related": true
}
```

---

## 📊 Analytics Endpoints

### GET `/api/analytics/dashboard`
Get dashboard analytics overview.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "total_tasks": 25,
  "completed_tasks": 18,
  "pending_tasks": 4,
  "in_progress_tasks": 3,
  "completion_rate": 72.0,
  "overdue_tasks": 1,
  "avg_completion_time": 4.5
}
```

### GET `/api/analytics/user-performance`
Get user performance analytics.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `user_id`: Specific user ID (managers only, optional)
- `period`: Time period (week, month, quarter)

**Response (200):**
```json
{
  "user_id": 1,
  "username": "john_doe",
  "tasks_completed": 12,
  "tasks_assigned": 15,
  "completion_rate": 80.0,
  "avg_completion_time": 3.2,
  "performance_score": 85,
  "rank": 2
}
```

### GET `/api/analytics/team-stats`
Get team performance statistics (managers only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "team_size": 8,
  "total_tasks": 45,
  "completed_tasks": 32,
  "team_completion_rate": 71.1,
  "top_performers": [
    {
      "user_id": 3,
      "username": "alice_smith",
      "performance_score": 92
    }
  ],
  "productivity_trend": "increasing"
}
```

### GET `/api/analytics/leaderboard`
Get performance leaderboard.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
[
  {
    "rank": 1,
    "user_id": 3,
    "username": "alice_smith",
    "performance_score": 92,
    "tasks_completed": 15,
    "completion_rate": 93.75
  },
  {
    "rank": 2,
    "user_id": 1,
    "username": "john_doe",
    "performance_score": 85,
    "tasks_completed": 12,
    "completion_rate": 80.0
  }
]
```

---

## 🏖️ Leave Management Endpoints

### GET `/api/leave/requests`
Get leave requests (filtered by user role).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status`: Filter by status (pending, approved, rejected)
- `user_id`: Filter by user (managers only)

**Response (200):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "username": "john_doe",
    "leave_type": "vacation",
    "start_date": "2024-02-01",
    "end_date": "2024-02-05",
    "days": 5,
    "reason": "Family vacation",
    "status": "pending",
    "created_at": "2024-01-15T00:00:00Z"
  }
]
```

### POST `/api/leave/requests`
Submit a new leave request.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "leave_type": "vacation" | "sick" | "personal" | "emergency",
  "start_date": "2024-02-01",
  "end_date": "2024-02-05",
  "reason": "Family vacation"
}
```

**Response (201):**
```json
{
  "id": 1,
  "user_id": 1,
  "leave_type": "vacation",
  "start_date": "2024-02-01",
  "end_date": "2024-02-05",
  "days": 5,
  "reason": "Family vacation",
  "status": "pending",
  "created_at": "2024-01-15T00:00:00Z"
}
```

### PATCH `/api/leave/requests/{request_id}/approve`
Approve a leave request (managers only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": 1,
  "status": "approved",
  "approved_by": 2,
  "approved_at": "2024-01-16T00:00:00Z"
}
```

### PATCH `/api/leave/requests/{request_id}/reject`
Reject a leave request (managers only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "reason": "Insufficient notice period"
}
```

**Response (200):**
```json
{
  "id": 1,
  "status": "rejected",
  "rejection_reason": "Insufficient notice period",
  "rejected_by": 2,
  "rejected_at": "2024-01-16T00:00:00Z"
}
```

### POST `/api/leave/transfer-tasks`
Transfer tasks when going on leave.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "leave_request_id": 1,
  "transfer_to_user_id": 3,
  "task_ids": [1, 2, 3]
}
```

**Response (200):**
```json
{
  "transferred_tasks": 3,
  "transfer_details": [
    {
      "task_id": 1,
      "original_assignee": 1,
      "new_assignee": 3,
      "transferred_at": "2024-01-20T00:00:00Z"
    }
  ]
}
```

---

## 🏥 Health Check Endpoints

### GET `/`
Basic API information.

**Response (200):**
```json
{
  "message": "AI-Powered Project Management System API",
  "version": "1.0.0",
  "status": "running"
}
```

### GET `/health`
Health check endpoint.

**Response (200):**
```json
{
  "status": "healthy"
}
```

---

## 🔒 Authentication

All endpoints (except `/`, `/health`, `/docs`, `/redoc`, and authentication endpoints) require a valid JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Token Expiration
- Access tokens expire after 30 minutes
- Refresh tokens by logging in again

### Role-Based Access Control

**Employee Access:**
- Can view their own tasks and profile
- Can update their own task status
- Can submit leave requests
- Can access analytics for their own performance

**Manager Access:**
- All employee permissions
- Can create, update, and delete tasks
- Can assign tasks to employees
- Can view all team tasks and analytics
- Can approve/reject leave requests
- Can access team statistics and leaderboards

---

## 📱 Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

## 🔧 Error Responses

```json
{
  "detail": "Error message description"
}
```

For validation errors:
```json
{
  "detail": [
    {
      "loc": ["field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```