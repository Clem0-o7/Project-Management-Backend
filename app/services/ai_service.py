import os
from google import genai
from google.genai import types
from app.core.config import settings
from typing import Optional

class AIService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = "gemma-3-27b-it"
    
    def generate_task_assignment(self, task_description: str, employees: list) -> dict:
        """AI-powered task assignment based on employee skills and workload"""
        employee_info = "\n".join([f"- {emp['name']}: {emp['position']}, Score: {emp['score']}, Success Rate: {emp['success_rate']}%" for emp in employees])
        
        prompt = f"""
        You are an AI project manager. Assign the following task to the most suitable employee:
        
        Task: {task_description}
        
        Available Employees:
        {employee_info}
        
        Consider:
        1. Employee skills and experience
        2. Current workload (lower score means more available)
        3. Success rate history
        4. Task complexity
        
        Respond in JSON format:
        {{
            "recommended_employee": "employee_name",
            "reasoning": "explanation",
            "difficulty_level": "easy|medium|hard",
            "estimated_hours": number,
            "risk_factors": ["factor1", "factor2"],
            "success_probability": percentage
        }}
        """
        
        try:
            contents = [types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )]
            
            response = ""
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig()
            ):
                if chunk.text:  # Check if chunk.text is not None
                    response += chunk.text
            
            return {"ai_response": response, "status": "success"}
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    def assess_task_risk(self, task_title: str, task_description: str, employee_profile: dict) -> dict:
        """Assess risk factors for a task assignment"""
        prompt = f"""
        Analyze the risk factors for this task assignment:
        
        Task: {task_title}
        Description: {task_description}
        
        Employee Profile:
        - Name: {employee_profile.get('name', 'Unknown')}
        - Position: {employee_profile.get('position', 'Unknown')}
        - Success Rate: {employee_profile.get('success_rate', 0)}%
        - Completed Tasks: {employee_profile.get('tasks_completed', 0)}
        
        Provide risk assessment (0.0 to 1.0) and recommendations:
        {{
            "risk_score": 0.0-1.0,
            "risk_factors": ["factor1", "factor2"],
            "recommendations": ["rec1", "rec2"],
            "monitoring_points": ["point1", "point2"]
        }}
        """
        
        try:
            contents = [types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )]
            
            response = ""
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig()
            ):
                if chunk.text:  # Check if chunk.text is not None
                    response += chunk.text
            
            return {"ai_response": response, "status": "success"}
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    def provide_status_feedback(self, task_title: str, status_report: str, progress: int) -> dict:
        """Provide AI feedback on task status reports"""
        prompt = f"""
        Review this task status report and provide constructive feedback:
        
        Task: {task_title}
        Progress: {progress}%
        Status Report: {status_report}
        
        Provide feedback in JSON format:
        {{
            "feedback": "constructive feedback",
            "suggestions": ["suggestion1", "suggestion2"],
            "concerns": ["concern1", "concern2"],
            "next_steps": ["step1", "step2"],
            "risk_level": "low|medium|high"
        }}
        """
        
        try:
            contents = [types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )]
            
            response = ""
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig()
            ):
                if chunk.text:  # Check if chunk.text is not None
                    response += chunk.text
            
            return {"ai_response": response, "status": "success"}
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    def chat_assistant(self, user_message: str, user_role: str) -> dict:
        """AI chat assistant for work-related queries"""
        context = f"""
        You are a helpful AI assistant for a project management system.
        User role: {user_role}
        
        Guidelines:
        - Only answer work and project management related questions
        - Be professional and helpful
        - Provide actionable advice
        - If the question is not work-related, politely redirect to work topics
        
        User Question: {user_message}
        """
        
        try:
            contents = [types.Content(
                role="user",
                parts=[types.Part.from_text(text=context)]
            )]
            
            response = ""
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig()
            ):
                if chunk.text:  # Check if chunk.text is not None
                    response += chunk.text
            
            return {"ai_response": response, "status": "success"}
        except Exception as e:
            return {"error": str(e), "status": "error"}

# Global AI service instance
ai_service = AIService()