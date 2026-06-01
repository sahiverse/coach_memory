# services/memory_service.py
from sqlalchemy.orm import Session as DBSession
from models.sql_models import User, Session, BehavioralFlag
from database.vector_db import get_coaching_memory_collection
from typing import Optional
import uuid

# ─────────────────────────────────────────────
# SQL READ FUNCTIONS
# ─────────────────────────────────────────────

def get_user(db: DBSession, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_all_sessions_for_user(db: DBSession, user_id: int) -> list[Session]:
    return (
        db.query(Session)
        .filter(Session.user_id == user_id)
        .order_by(Session.week_number.asc())
        .all()
    )

def get_latest_session(db: DBSession, user_id: int) -> Optional[Session]:
    return (
        db.query(Session)
        .filter(Session.user_id == user_id)
        .order_by(Session.week_number.desc())
        .first()
    )

def get_behavioral_flags(db: DBSession, user_id: int) -> list[BehavioralFlag]:
    return (
        db.query(BehavioralFlag)
        .filter(BehavioralFlag.user_id == user_id)
        .order_by(BehavioralFlag.week_identified.asc())
        .all()
    )

def compute_average_score(db: DBSession, user_id: int) -> Optional[float]:
    sessions = get_all_sessions_for_user(db, user_id)
    scored = [s.score for s in sessions if s.score is not None]
    if not scored:
        return None
    return round(sum(scored) / len(scored), 1)

def compute_score_delta(db: DBSession, user_id: int) -> Optional[float]:
    sessions = get_all_sessions_for_user(db, user_id)
    scored = [s.score for s in sessions if s.score is not None]
    if len(scored) < 2:
        return None
    return round(scored[-1] - scored[-2], 1)

# ─────────────────────────────────────────────
# SQL WRITE FUNCTIONS
# ─────────────────────────────────────────────

def create_user(db: DBSession, name: str, target_score: float, onboarding_summary: Optional[str] = None) -> User:
    user = User(name=name, target_score=target_score, onboarding_summary=onboarding_summary)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_session(db: DBSession, user_id: int, week_number: int, scenario_type: str = "job interview") -> Session:
    session = Session(user_id=user_id, week_number=week_number, scenario_type=scenario_type)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def update_session_after_roleplay(
    db: DBSession,
    session_id: int,
    score: float,
    feedback_summary: str
) -> Session:
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise ValueError(f"Session {session_id} not found")
    session.score = score
    session.feedback_summary = feedback_summary
    db.commit()
    db.refresh(session)
    return session

def add_behavioral_flag(db: DBSession, user_id: int, flag_text: str, week_identified: int) -> BehavioralFlag:
    flag = BehavioralFlag(user_id=user_id, flag_text=flag_text, week_identified=week_identified)
    db.add(flag)
    db.commit()
    db.refresh(flag)
    return flag

def advance_user_week(db: DBSession, user_id: int) -> User:
    user = get_user(db, user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    user.current_week = min(user.current_week + 1, 10)
    db.commit()
    db.refresh(user)
    return user

# ─────────────────────────────────────────────
# CHROMADB READ FUNCTIONS
# ─────────────────────────────────────────────

def get_semantic_memories(user_id: int, n_results: int = 3) -> list[str]:
    """
    Retrieves the most relevant past feedback summaries for a user
    from the vector database.
    Returns a list of document strings.
    """
    collection = get_coaching_memory_collection()
    try:
        results = collection.query(
            query_texts=[f"coaching history for user {user_id}"],
            n_results=n_results,
            where={"user_id": str(user_id)}
        )
        if results and results["documents"]:
            return results["documents"][0]  # list of matching doc strings
        return []
    except Exception:
        return []

# ─────────────────────────────────────────────
# CHROMADB WRITE FUNCTIONS
# ─────────────────────────────────────────────

def store_onboarding_memory(user_id: int, onboarding_text: str) -> None:
    """
    Stores the onboarding summary for a user in ChromaDB.
    Called once when a user is created.
    """
    collection = get_coaching_memory_collection()
    collection.upsert(
        ids=[f"onboarding_{user_id}"],
        documents=[onboarding_text],
        metadatas=[{"user_id": str(user_id), "type": "onboarding"}]
    )

def store_session_feedback_memory(user_id: int, week_number: int, feedback_text: str) -> None:
    """
    Stores post-session feedback summary in ChromaDB so future sessions
    can retrieve relevant coaching history via semantic search.
    """
    collection = get_coaching_memory_collection()
    doc_id = f"feedback_{user_id}_week{week_number}_{uuid.uuid4().hex[:6]}"
    collection.upsert(
        ids=[doc_id],
        documents=[feedback_text],
        metadatas=[{
            "user_id": str(user_id),
            "week_number": str(week_number),
            "type": "session_feedback"
        }]
    )
