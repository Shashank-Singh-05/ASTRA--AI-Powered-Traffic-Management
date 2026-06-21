"""ASTRA AI Copilot Router."""

from fastapi import APIRouter, Depends
from backend.schemas.prediction import ChatRequest, ChatResponse
from backend.models.user import User
from backend.middleware.auth import get_current_active_user

import os
import google.generativeai as genai

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

router = APIRouter(prefix="/api/chat", tags=["AI Copilot"])

SYSTEM_PROMPT = """You are ASTRA Copilot, an expert AI assistant for Bengaluru Traffic Police.
You help command center operators manage traffic incidents, deploy resources, and mitigate congestion.
Always provide concise, actionable, and highly professional advice.
Whenever you provide an answer, end your response with exactly 2 or 3 short follow-up actions the user might want to take, formatted exactly like this on separate lines at the very end:
SUGGESTED: Show high risk events
SUGGESTED: Analyze corridor stress
"""

@router.post("", response_model=ChatResponse)
async def chat_with_copilot(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Interact with the AI Copilot for traffic management advice."""
    query = request.message
    
    if not api_key:
        return ChatResponse(
            response="Error: GEMINI_API_KEY is not configured in the backend environment. Please set it in your .env file and restart the server.",
            similar_events=[],
            suggested_actions=["Check .env file", "Restart Docker containers"],
            confidence=0.0
        )
        
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Combine system prompt and user query
        full_prompt = f"{SYSTEM_PROMPT}\n\nOperator Query: {query}\n\nResponse:"
        
        # Call Gemini API
        response = model.generate_content(full_prompt)
        response_text = response.text
        
        # Parse out suggested actions
        lines = response_text.strip().split('\n')
        actual_response = []
        suggested = []
        
        for line in lines:
            if line.startswith("SUGGESTED:"):
                suggested.append(line.replace("SUGGESTED:", "").strip())
            else:
                actual_response.append(line)
                
        # Fallback suggestions if Gemini failed to format them correctly
        if not suggested:
            suggested = ["Show active events", "Generate deployment plan"]
            
        final_text = '\n'.join(actual_response).strip()
        
        return ChatResponse(
            response=final_text,
            similar_events=[],
            suggested_actions=suggested[:3],
            confidence=0.95
        )
        
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        return ChatResponse(
            response="I'm sorry, I encountered an error connecting to the AI brain. Please try again later.",
            similar_events=[],
            suggested_actions=["Check API Quota", "Check internet connection"],
            confidence=0.1
        )
