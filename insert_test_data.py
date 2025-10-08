#!/usr/bin/env python3
"""
Script to insert test data into the project management system
"""
import requests
import json
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = "https://ai-project-mgmt-backend-113c31864f66.herokuapp.com"

def create_test_users():
    """Create test users"""
    users = [
        {
            "email": "manager@test.com",
            "password": "manager123",
            "role": "manager"
        },
        {
            "email": "employee1@test.com", 
            "password": "employee123",
            "role": "employee"
        },
        {
            "email": "employee2@test.com",
            "password": "employee123", 
            "role": "employee"
        },
        {
            "email": "employee3@test.com",
            "password": "employee123",
            "role": "employee"
        }
    ]
    
    created_users = []
    for user_data in users:
        try:
            response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
            if response.status_code == 201:
                created_user = response.json()
                created_users.append(created_user)
                print(f"✅ Created user: {user_data['email']} (ID: {created_user['id']})")
            else:
                print(f"❌ Failed to create user {user_data['email']}: {response.text}")
        except Exception as e:
            print(f"❌ Error creating user {user_data['email']}: {e}")
    
    return created_users

def get_auth_token(email, password):
    """Get authentication token for a user"""
    try:
        response = requests.post(f"{BASE_URL}/api/auth/token", data={
            "username": email,
            "password": password
        })
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"❌ Failed to authenticate {email}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error authenticating {email}: {e}")
        return None

def create_test_tasks(manager_token, employee_ids):
    """Create test tasks"""
    tasks = [
        {
            "title": "Implement User Authentication",
            "description": "Develop JWT-based authentication system with role-based access control",
            "priority": "high",
            "assigned_to": employee_ids[0],
            "due_date": (datetime.now() + timedelta(days=7)).isoformat()
        },
        {
            "title": "Design Database Schema",
            "description": "Create comprehensive database schema for project management system",
            "priority": "medium",
            "assigned_to": employee_ids[1],
            "due_date": (datetime.now() + timedelta(days=5)).isoformat()
        },
        {
            "title": "Implement Task Management API",
            "description": "Develop CRUD operations for task management with proper validation",
            "priority": "high",
            "assigned_to": employee_ids[0],
            "due_date": (datetime.now() + timedelta(days=10)).isoformat()
        },
        {
            "title": "Setup CI/CD Pipeline",
            "description": "Configure automated testing and deployment pipeline",
            "priority": "medium",
            "assigned_to": employee_ids[2],
            "due_date": (datetime.now() + timedelta(days=14)).isoformat()
        },
        {
            "title": "Frontend Development",
            "description": "Build responsive Flutter frontend for the application",
            "priority": "high",
            "assigned_to": employee_ids[1],
            "due_date": (datetime.now() + timedelta(days=21)).isoformat()
        },
        {
            "title": "API Documentation",
            "description": "Create comprehensive API documentation with examples",
            "priority": "low",
            "assigned_to": employee_ids[2],
            "due_date": (datetime.now() + timedelta(days=12)).isoformat()
        }
    ]
    
    headers = {"Authorization": f"Bearer {manager_token}"}
    created_tasks = []
    
    for task_data in tasks:
        try:
            response = requests.post(f"{BASE_URL}/api/tasks/", json=task_data, headers=headers)
            if response.status_code == 201:
                created_task = response.json()
                created_tasks.append(created_task)
                print(f"✅ Created task: {task_data['title']} (ID: {created_task['id']})")
            else:
                print(f"❌ Failed to create task {task_data['title']}: {response.text}")
        except Exception as e:
            print(f"❌ Error creating task {task_data['title']}: {e}")
    
    return created_tasks

def update_task_statuses(employee_tokens, task_ids):
    """Update some tasks to different statuses"""
    status_updates = [
        {"task_id": task_ids[0], "status": "in_progress", "notes": "Started working on authentication middleware"},
        {"task_id": task_ids[1], "status": "completed", "notes": "Database schema design completed and reviewed"},
        {"task_id": task_ids[2], "status": "in_progress", "notes": "CRUD operations 50% complete"},
    ]
    
    for i, update in enumerate(status_updates[:len(employee_tokens)]):
        headers = {"Authorization": f"Bearer {employee_tokens[i % len(employee_tokens)]}"}
        try:
            response = requests.post(
                f"{BASE_URL}/api/tasks/{update['task_id']}/status",
                json={"status": update["status"], "notes": update["notes"]},
                headers=headers
            )
            if response.status_code == 200:
                print(f"✅ Updated task {update['task_id']} status to {update['status']}")
            else:
                print(f"❌ Failed to update task {update['task_id']}: {response.text}")
        except Exception as e:
            print(f"❌ Error updating task {update['task_id']}: {e}")

def create_leave_requests(employee_tokens):
    """Create test leave requests"""
    leave_requests = [
        {
            "leave_type": "vacation",
            "start_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "end_date": (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d"),
            "reason": "Family vacation"
        },
        {
            "leave_type": "sick",
            "start_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
            "end_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "reason": "Medical appointment"
        }
    ]
    
    for i, leave_data in enumerate(leave_requests[:len(employee_tokens)]):
        headers = {"Authorization": f"Bearer {employee_tokens[i]}"}
        try:
            response = requests.post(f"{BASE_URL}/api/leave/requests", json=leave_data, headers=headers)
            if response.status_code == 201:
                created_request = response.json()
                print(f"✅ Created leave request: {leave_data['leave_type']} (ID: {created_request['id']})")
            else:
                print(f"❌ Failed to create leave request: {response.text}")
        except Exception as e:
            print(f"❌ Error creating leave request: {e}")

def main():
    print("🚀 Inserting test data into the project management system...")
    print("=" * 60)
    
    # Create test users
    print("\n📝 Creating test users...")
    users = create_test_users()
    
    # If users already exist, create mock user data
    if len(users) < 4:
        print("ℹ️ Users already exist. Using existing user data...")
        users = [
            {"id": 1, "email": "manager@test.com", "role": "manager"},
            {"id": 2, "email": "employee1@test.com", "role": "employee"},
            {"id": 3, "email": "employee2@test.com", "role": "employee"},
            {"id": 4, "email": "employee3@test.com", "role": "employee"}
        ]
    
    # Get authentication tokens
    print("\n🔐 Getting authentication tokens...")
    manager_token = get_auth_token("manager@test.com", "manager123")
    employee_tokens = [
        get_auth_token("employee1@test.com", "employee123"),
        get_auth_token("employee2@test.com", "employee123"),
        get_auth_token("employee3@test.com", "employee123")
    ]
    
    if not manager_token or not all(employee_tokens):
        print("❌ Failed to get authentication tokens. Exiting...")
        return
    
    # Extract employee IDs
    employee_ids = [user["id"] for user in users if user["role"] == "employee"]
    
    # Create test tasks
    print("\n📋 Creating test tasks...")
    tasks = create_test_tasks(manager_token, employee_ids)
    
    if tasks:
        task_ids = [task["id"] for task in tasks]
        
        # Update task statuses
        print("\n🔄 Updating task statuses...")
        update_task_statuses(employee_tokens, task_ids)
    
    # Create leave requests
    print("\n🏖️ Creating leave requests...")
    create_leave_requests(employee_tokens)
    
    print("\n✅ Test data insertion completed!")
    print("=" * 60)
    print("\n📊 Summary:")
    print(f"👥 Users created: {len(users)}")
    print(f"📋 Tasks created: {len(tasks) if tasks else 0}")
    print("\n🔑 Test accounts:")
    print("Manager: manager@test.com / manager123")
    print("Employee 1: employee1@test.com / employee123")
    print("Employee 2: employee2@test.com / employee123") 
    print("Employee 3: employee3@test.com / employee123")

if __name__ == "__main__":
    main()