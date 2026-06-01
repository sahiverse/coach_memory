# services/context_service.py
from sqlalchemy.orm import Session as DBSession
from services.memory_service import (
    get_user,
    compute_average_score,
    compute_score_delta,
    get_behavioral_flags,
    get_semantic_memories,
)
from schemas.pydantic_schemas import CoachingContext

def build_coaching_context(db: DBSession, user_id: int) -> CoachingContext:
    """
    Aggregates all three memory layers into a single CoachingContext object.

    Layer 1 (Semantic Memory)  → ChromaDB: past feedback summaries
    Layer 2 (Episodic Memory)  → SQL: scores, week, target, flags
    Layer 3 (Working Memory)   → NOT handled here; managed per-session in Phase 3

    Returns a CoachingContext Pydantic model ready to be injected into prompts.
    """
    user = get_user(db, user_id)
    if not user:
        raise ValueError(f"User with id {user_id} not found")

    # --- Layer 2: SQL facts ---
    avg_score = compute_average_score(db, user_id)
    score_delta = compute_score_delta(db, user_id)
    flags = get_behavioral_flags(db, user_id)
    flag_texts = [f.flag_text for f in flags]

    # --- Layer 1: ChromaDB semantic memories ---
    past_summaries = get_semantic_memories(user_id, n_results=3)

    # --- Build a human-readable progress narrative for prompt injection ---
    progress_narrative = _build_progress_narrative(
        name=user.name,
        current_week=user.current_week,
        target_score=user.target_score,
        avg_score=avg_score,
        score_delta=score_delta,
        flags=flag_texts,
        past_summaries=past_summaries,
        onboarding_summary=user.onboarding_summary
    )

    return CoachingContext(
        user_name=user.name,
        current_week=user.current_week,
        target_score=user.target_score,
        average_score=avg_score,
        score_delta=score_delta,
        behavioral_flags=flag_texts,
        past_feedback_summaries=past_summaries,
        onboarding_summary=user.onboarding_summary,
        progress_narrative=progress_narrative
    )


def _build_progress_narrative(
    name: str,
    current_week: int,
    target_score: float,
    avg_score: float | None,
    score_delta: float | None,
    flags: list[str],
    past_summaries: list[str],
    onboarding_summary: str | None
) -> str:
    """
    Converts structured data into a concise paragraph that can be injected
    directly into an LLM system prompt. Written to be read by the AI as
    factual coaching context, not by the user.
    """
    lines = []

    lines.append(f"USER COACHING PROFILE — {name.upper()}")
    lines.append(f"Program week: {current_week} of 10. Target score: {target_score}/100.")

    if avg_score is not None:
        lines.append(f"Current average score across all sessions: {avg_score}/100.")
    else:
        lines.append("No scored sessions yet. This is an early-stage user.")

    if score_delta is not None:
        direction = "improved" if score_delta >= 0 else "declined"
        lines.append(f"Score {direction} by {abs(score_delta)} points since last session.")

    if flags:
        flags_str = "; ".join(flags)
        lines.append(f"Recurring behavioral patterns identified: {flags_str}.")
    else:
        lines.append("No recurring behavioral patterns identified yet.")

    if onboarding_summary:
        lines.append(f"Onboarding background: {onboarding_summary}")

    if past_summaries:
        lines.append("Relevant coaching history from previous sessions:")
        for i, summary in enumerate(past_summaries, 1):
            lines.append(f"  [{i}] {summary}")

    lines.append(
        "\nINSTRUCTION: Use this profile to personalize every response. "
        "Reference specific patterns and history when relevant. "
        "Never mention that you are reading from a database."
    )

    return "\n".join(lines)
