# api/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.sql_db import SessionLocal
from services.context_service import build_coaching_context
from services.prompt_service import build_roleplay_system_prompt, build_feedback_system_prompt, build_session_opening
from services.llm_service import generate_response, generate_structured_response
from services.memory_service import get_user
from schemas.pydantic_schemas import SessionCreate, SessionUpdate
from models.sql_models import Session as SessionModel
from pydantic import BaseModel
from typing import Optional
import json

router = APIRouter()

# ── In-memory session store (keyed by user_id) ──────────────────────────────
# Holds active roleplay state between /session/start and /session/end
_active_sessions: dict[int, dict] = {}


# ── Dependency ────────────────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Request/Response models ───────────────────────────────────────────────────
class RoleplayTurnRequest(BaseModel):
    user_id: int
    user_message: str

class EndSessionRequest(BaseModel):
    user_id: int
    score: float


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/users/{user_id}")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Returns the coaching profile for a user."""
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    context = build_coaching_context(db, user_id)
    return context


@router.post("/session/start")
def start_session(payload: SessionCreate, db: Session = Depends(get_db)):
    """
    Initializes a coaching session for a user.
    - Builds context from all three memory layers
    - Generates a personalized session opening from Vani
    - Stores the roleplay system prompt in memory for this session
    """
    user = get_user(db, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Aggregate all memory layers
    context = build_coaching_context(db, payload.user_id)

    # Build prompts
    roleplay_system_prompt = build_roleplay_system_prompt(context)
    opening_message = build_session_opening(context)

    # Create a session record in SQL
    session = SessionModel(
        user_id=payload.user_id,
        week_number=payload.week_number,
        scenario_type=payload.scenario_type,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Store active session state in memory
    _active_sessions[payload.user_id] = {
        "session_id": session.id,
        "system_prompt": roleplay_system_prompt,
        "context": context,
        "history": [],  # conversation turns go here
    }

    return {
        "session_id": session.id,
        "opening_message": opening_message,
        "user_name": context.user_name,
        "week": context.current_week,
        "current_score": context.average_score,
        "target_score": context.target_score,
    }


@router.post("/session/roleplay")
def roleplay_turn(payload: RoleplayTurnRequest, db: Session = Depends(get_db)):
    """
    Handles one turn of the adversarial roleplay.
    - Appends the user's message to conversation history
    - Calls the LLM with the full history and roleplay system prompt
    - Returns the interviewer's response
    """
    active = _active_sessions.get(payload.user_id)
    if not active:
        raise HTTPException(
            status_code=400,
            detail="No active session found for this user. Call /session/start first."
        )

    # Append user turn to history
    active["history"].append({
        "role": "user",
        "content": payload.user_message
    })

    # Generate interviewer response
    interviewer_reply = generate_response(
        system_prompt=active["system_prompt"],
        messages=active["history"]
    )

    # Append assistant turn to history
    active["history"].append({
        "role": "assistant",
        "content": interviewer_reply
    })

    return {
        "interviewer_response": interviewer_reply,
        "turn_count": len(active["history"]) // 2,
    }


@router.post("/session/end")
def end_session(payload: EndSessionRequest, db: Session = Depends(get_db)):
    """
    Ends the session and produces structured feedback.
    - Generates 4-part feedback report from the full conversation
    - Writes score and feedback to SQL
    - Stores feedback summary in ChromaDB for future sessions
    """
    from services.memory_service import store_session_feedback_memory

    active = _active_sessions.get(payload.user_id)
    if not active:
        raise HTTPException(
            status_code=400,
            detail="No active session found for this user."
        )

    context = active["context"]
    history = active["history"]

    # Build feedback prompt with full conversation as context
    conversation_text = "\n".join(
        f"{'Candidate' if m['role'] == 'user' else 'Interviewer'}: {m['content']}"
        for m in history
    )

    feedback_system_prompt = build_feedback_system_prompt(context)
    feedback = generate_structured_response(
        system_prompt=feedback_system_prompt,
        messages=[{
            "role": "user",
            "content": f"Here is the full session transcript:\n\n{conversation_text}\n\nThe candidate's score for this session is {payload.score}/100. Please generate the feedback report."
        }]
    )

    # Write score and feedback to SQL
    session = db.query(SessionModel).filter(
        SessionModel.id == active["session_id"]
    ).first()
    session.score = payload.score
    session.feedback_summary = feedback
    db.commit()

    # Store in ChromaDB for future semantic retrieval
    store_session_feedback_memory(
        user_id=payload.user_id,
        week_number=context.current_week,
        feedback_text=feedback
    )

    # Clear active session
    del _active_sessions[payload.user_id]

    return {
        "session_id": active["session_id"],
        "score": payload.score,
        "feedback_report": feedback,
    }