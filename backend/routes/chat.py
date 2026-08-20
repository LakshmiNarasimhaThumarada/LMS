from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage

from backend.agents.supervisor import app_graph
from backend.utils.auth import require_jwt

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    pdf_id: Optional[str] = None
    conversation_history: Optional[List[ChatMessage]] = None

class ChatResponse(BaseModel):
    response: str
    next_node: str
    active_quiz_data: Optional[dict] = None

@router.post("", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    user = Depends(require_jwt)
):
    try:
        # Convert history format to LangChain message structures
        history = []
        if request.conversation_history:
            for msg in request.conversation_history:
                if msg.role == "user":
                    history.append(HumanMessage(content=msg.content))
                else:
                    history.append(AIMessage(content=msg.content))
        
        # Invoke the LangGraph agent graph
        state = {
            "message": request.message,
            "user_id": str(user['id']),
            "pdf_id": request.pdf_id or "",
            "conversation_history": history,
            "agent_response": "",
            "active_quiz_data": {},
            "student_answers": [],
            "quiz_results": {},
            "weak_areas_summary": [],
            "next_node": ""
        }
        
        # Invoke LangGraph
        result = app_graph.invoke(state)
        
        return ChatResponse(
            response=result.get("agent_response", ""),
            next_node=result.get("next_node", ""),
            active_quiz_data=result.get("active_quiz_data")
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
