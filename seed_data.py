# seed_data.py
"""
Run this script once to populate both databases with mock data.
Usage: python seed_data.py
"""
from database.sql_db import SessionLocal, create_all_tables
from services.memory_service import (
    create_user,
    create_session,
    update_session_after_roleplay,
    add_behavioral_flag,
    store_onboarding_memory,
    store_session_feedback_memory,
    advance_user_week,
)

def seed():
    create_all_tables()
    db = SessionLocal()

    try:
        print("🌱 Seeding mock users...")

        # ─────────────────────────────────────────────
        # USER 1: Priya — Week 3, strong history
        # This is the "impressive demo" user
        # ─────────────────────────────────────────────
        priya = create_user(
            db=db,
            name="Priya Sharma",
            target_score=85.0,
            onboarding_summary=(
                "Priya is a senior product manager preparing for VP-level interviews. "
                "She has 6 years of experience but struggles with executive presence under pressure. "
                "Primary goals: reduce filler words, improve conciseness, project confidence in adversarial Q&A."
            )
        )

        # Store onboarding in ChromaDB
        store_onboarding_memory(
            user_id=priya.id,
            onboarding_text=priya.onboarding_summary
        )

        # Week 1 session
        s1 = create_session(db, priya.id, week_number=1, scenario_type="job interview")
        feedback_w1 = (
            "Week 1 — Priya showed strong content knowledge but used 'um' and 'uh' 14 times in a 10-minute session. "
            "She spoke 22% faster than her baseline when asked about conflict resolution. "
            "Recommended focus: awareness drills for filler words before Week 2."
        )
        update_session_after_roleplay(db, s1.id, score=58.0, feedback_summary=feedback_w1)
        store_session_feedback_memory(priya.id, 1, feedback_w1)

        # Week 2 session
        s2 = create_session(db, priya.id, week_number=2, scenario_type="job interview")
        feedback_w2 = (
            "Week 2 — Filler words reduced from 14 to 9, showing progress. "
            "However, Priya still accelerates her speech when pressed on leadership decisions — a recurring pattern. "
            "She deflected two follow-up questions rather than holding her position. "
            "Recommended focus: grounding techniques before answering pressure questions."
        )
        update_session_after_roleplay(db, s2.id, score=64.0, feedback_summary=feedback_w2)
        store_session_feedback_memory(priya.id, 2, feedback_w2)

        # Behavioral flags
        add_behavioral_flag(db, priya.id, "speaks 20-25% faster when under questioning pressure", week_identified=1)
        add_behavioral_flag(db, priya.id, "uses filler words 'um' and 'uh' excessively — improving but not resolved", week_identified=1)
        add_behavioral_flag(db, priya.id, "deflects follow-up questions on leadership decisions instead of holding position", week_identified=2)

        # Advance to week 3
        advance_user_week(db, priya.id)
        advance_user_week(db, priya.id)
        # (she's now at week 3, ready for her next session)

        print(f"✅ User 1 created: {priya.name} (id={priya.id}, week={priya.current_week})")

        # ─────────────────────────────────────────────
        # USER 2: Arjun — Week 1, no history
        # This is the "before" contrast user
        # ─────────────────────────────────────────────
        arjun = create_user(
            db=db,
            name="Arjun Mehta",
            target_score=80.0,
            onboarding_summary=(
                "Arjun is a software engineer moving into a tech lead role. "
                "He has never done formal communication training. "
                "Primary goals: structure answers using frameworks like STAR, build confidence presenting to non-technical stakeholders."
            )
        )

        store_onboarding_memory(
            user_id=arjun.id,
            onboarding_text=arjun.onboarding_summary
        )

        print(f"✅ User 2 created: {arjun.name} (id={arjun.id}, week={arjun.current_week})")

        print("\n🎉 Seed complete. Summary:")
        print(f"   Priya (id={priya.id}): Week 3, avg score ~61, 3 behavioral flags, rich history in both DBs")
        print(f"   Arjun (id={arjun.id}): Week 1, no sessions yet, onboarding in ChromaDB only")
        print("\nTo start the API: uvicorn main:app --reload")
        print("Health check: http://localhost:8000/health")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
