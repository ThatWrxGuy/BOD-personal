"""Chat API routes."""
import uuid
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.chat.chat_types import ChatSession, ChatMessage, IntentType, ChatMessageStatus, ChatSessionStatus
from app.chat.intent_classifier import get_intent_classifier
from app.chat.command_interpreter import get_command_interpreter
from app.observability import increment
from app.observability.metrics_service import MetricDomain

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message")
async def send_message(
    message: str = Query(..., description="User message"),
    session_id: Optional[str] = Query(None, description="Session ID for continuation"),
    session: AsyncSession = Depends(get_db),
):
    """Send a chat message and get a response."""
    
    from sqlalchemy import select
    
    # Get or create session
    chat_session = None
    if session_id:
        result = await session.execute(
            select(ChatSession).where(ChatSession.id == uuid.UUID(session_id))
        )
        chat_session = result.scalar_one_or_none()
    
    if not chat_session:
        # Create new session
        chat_session = ChatSession(
            started_at=datetime.utcnow(),
            status=ChatSessionStatus.ACTIVE,
        )
        session.add(chat_session)
        await session.commit()
        await session.refresh(chat_session)
    
    # Create message
    chat_message = ChatMessage(
        session_id=chat_session.id,
        message=message,
        status=ChatMessageStatus.PROCESSING,
    )
    session.add(chat_message)
    await session.commit()
    await session.refresh(chat_message)
    
    try:
        # Classify intent
        classifier = await get_intent_classifier()
        intent, confidence = classifier.classify(message)
        params = classifier.extract_parameters(message, intent)
        
        # Update message with intent
        chat_message.intent = intent
        chat_message.intent_confidence = confidence
        
        # Execute command
        interpreter = await get_command_interpreter(session)
        result = await interpreter.execute(intent, params)
        
        # Generate response
        response = _generate_response(intent, result)
        
        chat_message.response = response
        chat_message.status = ChatMessageStatus.COMPLETED
        chat_message.command_type = intent
        chat_message.command_result = result
        
        # Update session
        chat_session.message_count += 1
        chat_session.last_message_at = datetime.utcnow()
        
        await session.commit()
        
        increment("messages_processed", domain=MetricDomain.SYSTEM)
        
        return {
            "session_id": str(chat_session.id),
            "message_id": str(chat_message.id),
            "response": response,
            "intent": intent,
            "confidence": confidence,
            "result": result,
        }
    
    except Exception as e:
        chat_message.status = ChatMessageStatus.FAILED
        chat_message.response = f"Error processing message: {str(e)}"
        await session.commit()
        raise HTTPException(status_code=500, detail=str(e))


def _generate_response(intent: str, result: dict) -> str:
    """Generate a natural language response."""
    
    result_type = result.get("type", "general")
    
    if result_type == "risks":
        count = result.get("count", 0)
        if count == 0:
            return "No high-priority risks detected at this time."
        return f"I found {count} potential risks. The most significant include: " + ", ".join([i["title"] for i in result.get("items", [])[:3]])
    
    elif result_type == "opportunities":
        count = result.get("count", 0)
        if count == 0:
            return "No specific opportunities detected at this time."
        return f"I found {count} potential opportunities. Key ones include: " + ", ".join([i["title"] for i in result.get("items", [])[:3]])
    
    elif result_type == "simulation":
        return f"Simulation completed. Recommended scenario: {result.get('recommended', 'N/A')}. Run details to see all scenarios."
    
    elif result_type == "research":
        return f"Research started on '{result.get('topic')}'. Task ID: {result.get('task_id')}"
    
    elif result_type == "plan":
        return f"Strategic plan created: '{result.get('title')}'. Plan ID: {result.get('plan_id')}"
    
    elif result_type == "review":
        return f"Strategic review initiated. Review ID: {result.get('review_id')}"
    
    elif result_type == "financial_status":
        liquidity_status = result.get("liquidity", {}).get("status", "unknown")
        days = result.get("liquidity", {}).get("days_coverage", 0)
        return f"Financial status: Liquidity is {liquidity_status} with {days} days of coverage."
    
    elif result_type == "goals":
        count = result.get("count", 0)
        return f"You have {count} goals tracked. " + ", ".join([g["name"] for g in result.get("items", [])[:5]])
    
    elif result_type == "bills":
        count = result.get("count", 0)
        total = result.get("total", 0)
        return f"You have {count} upcoming bills totaling ${total:.2f}."
    
    elif result_type == "liquidity":
        status = result.get("status", "unknown")
        days = result.get("days_of_coverage", 0)
        return f"Liquidity status: {status}. Days of coverage: {days}."
    
    elif result_type == "system_status":
        return "PSIE is operational. Active modules: " + ", ".join(result.get("modules", []))
    
    return result.get("message", "Command executed successfully.")


@router.get("/sessions")
async def list_sessions(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """List chat sessions."""
    
    from sqlalchemy import select, desc
    
    result = await session.execute(
        select(ChatSession).order_by(desc(ChatSession.last_message_at)).limit(limit)
    )
    sessions = list(result.scalars().all())
    
    return {
        "sessions": [
            {
                "id": str(s.id),
                "status": s.status,
                "message_count": s.message_count,
                "last_message_at": s.last_message_at.isoformat() if s.last_message_at else None,
                "started_at": s.started_at.isoformat() if s.started_at else None,
            }
            for s in sessions
        ]
    }


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db),
):
    """Get chat session details."""
    
    from sqlalchemy import select
    
    result = await session.execute(
        select(ChatSession).where(ChatSession.id == session_id)
    )
    chat_session = result.scalar_one_or_none()
    
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get messages
    msg_result = await session.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .limit(limit)
    )
    messages = list(msg_result.scalars().all())
    
    return {
        "session": {
            "id": str(chat_session.id),
            "status": chat_session.status,
            "message_count": chat_session.message_count,
            "started_at": chat_session.started_at.isoformat() if chat_session.started_at else None,
        },
        "messages": [
            {
                "id": str(m.id),
                "message": m.message,
                "response": m.response,
                "intent": m.intent,
                "intent_confidence": m.intent_confidence,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ],
    }


@router.get("/history")
async def get_chat_history(
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_db),
):
    """Get recent chat history."""
    
    from sqlalchemy import select, desc
    
    result = await session.execute(
        select(ChatMessage)
        .order_by(desc(ChatMessage.created_at))
        .limit(limit)
    )
    messages = list(result.scalars().all())
    
    return {
        "messages": [
            {
                "id": str(m.id),
                "session_id": str(m.session_id),
                "message": m.message,
                "response": m.response,
                "intent": m.intent,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ]
    }
