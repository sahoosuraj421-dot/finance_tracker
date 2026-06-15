from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.transaction import ChatMessage
from app.schemas.transaction import ChatRequest, ChatResponse
from app.services.chat_agent import new_session_id, run_chat

router = APIRouter(prefix="/api/chat", tags=["chat"])

# In-memory session history (persisted to DB for durability)
_session_cache: dict[str, list[dict]] = {}


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    session_id = payload.session_id or new_session_id()

    if session_id not in _session_cache:
        stored = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
            .all()
        )
        _session_cache[session_id] = [{"role": m.role, "content": m.content} for m in stored]

    history = _session_cache[session_id]

    try:
        reply, tool_calls = run_chat(db, payload.message, history)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

    history.append({"role": "user", "content": payload.message})
    history.append({"role": "assistant", "content": reply})
    _session_cache[session_id] = history[-20:]

    db.add(ChatMessage(session_id=session_id, role="user", content=payload.message))
    db.add(ChatMessage(session_id=session_id, role="assistant", content=reply))
    db.commit()

    return ChatResponse(reply=reply, session_id=session_id, tool_calls=tool_calls)


@router.get("/history/{session_id}")
def get_history(session_id: str, db: Session = Depends(get_db)):
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    return [{"role": m.role, "content": m.content, "created_at": m.created_at} for m in messages]
