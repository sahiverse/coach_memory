# app.py — Vani.coach Streamlit Frontend
import streamlit as st
import requests
import json

# ── Config ────────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="Vani.coach",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Background */
.stApp {
    background-color: #0f0f0f;
    color: #f0ece4;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #161616;
    border-right: 1px solid #2a2a2a;
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }

/* Logo */
.vani-logo {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #f0ece4;
    letter-spacing: -0.5px;
    margin-bottom: 0.2rem;
}
.vani-tagline {
    font-size: 0.75rem;
    color: #666;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

/* Score ring */
.score-block {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    margin-bottom: 1rem;
}
.score-number {
    font-family: 'DM Serif Display', serif;
    font-size: 3.5rem;
    color: #e8d5b0;
    line-height: 1;
}
.score-label {
    font-size: 0.7rem;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 0.3rem;
}
.score-target {
    font-size: 0.85rem;
    color: #888;
    margin-top: 0.5rem;
}

/* Progress bar */
.progress-track {
    background: #2a2a2a;
    border-radius: 99px;
    height: 6px;
    margin: 0.8rem 0;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, #c9a96e, #e8d5b0);
    transition: width 0.6s ease;
}

/* Flag card */
.flag-card {
    background: #1a1a1a;
    border-left: 3px solid #c9a96e;
    border-radius: 0 8px 8px 0;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
    color: #ccc;
    line-height: 1.5;
}

/* Section headers */
.section-label {
    font-size: 0.65rem;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-bottom: 0.75rem;
    margin-top: 1.5rem;
}

/* Chat bubbles */
.chat-user {
    background: #1e2a1e;
    border: 1px solid #2a3d2a;
    border-radius: 12px 12px 4px 12px;
    padding: 0.875rem 1.1rem;
    margin: 0.5rem 0 0.5rem 3rem;
    font-size: 0.9rem;
    color: #c8e6c8;
    line-height: 1.6;
}
.chat-interviewer {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 12px 12px 12px 4px;
    padding: 0.875rem 1.1rem;
    margin: 0.5rem 3rem 0.5rem 0;
    font-size: 0.9rem;
    color: #c8c8e6;
    line-height: 1.6;
}
.chat-role {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 0.4rem;
    opacity: 0.5;
}

/* Feedback sections */
.feedback-block {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.feedback-number {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #c9a96e;
    opacity: 0.4;
    line-height: 1;
}
.feedback-title {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #c9a96e;
    margin-bottom: 0.6rem;
}
.feedback-text {
    font-size: 0.9rem;
    color: #ccc;
    line-height: 1.7;
}

/* Buttons */
.stButton > button {
    background: #c9a96e !important;
    color: #0f0f0f !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.5px !important;
    padding: 0.6rem 1.5rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover {
    opacity: 0.85 !important;
}

/* Text input */
.stTextInput > div > div > input {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    color: #f0ece4 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: #c9a96e !important;
    box-shadow: 0 0 0 2px rgba(201,169,110,0.15) !important;
}

/* Select box */
.stSelectbox > div > div {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    color: #f0ece4 !important;
}

/* Delta badge */
.delta-up {
    display: inline-block;
    background: #1e2a1e;
    color: #6fcf6f;
    border-radius: 99px;
    padding: 0.2rem 0.75rem;
    font-size: 0.8rem;
    font-weight: 600;
}
.delta-down {
    display: inline-block;
    background: #2a1e1e;
    color: #cf6f6f;
    border-radius: 99px;
    padding: 0.2rem 0.75rem;
    font-size: 0.8rem;
    font-weight: 600;
}

/* Week badge */
.week-badge {
    display: inline-block;
    border: 1px solid #2a2a2a;
    border-radius: 99px;
    padding: 0.2rem 0.75rem;
    font-size: 0.75rem;
    color: #888;
    letter-spacing: 1px;
}

/* Divider */
.vani-divider {
    border: none;
    border-top: 1px solid #2a2a2a;
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key, default in {
    "screen": "profile",        # profile | session | feedback
    "session_id": None,
    "history": [],              # list of {role, content}
    "opening_message": None,
    "feedback_report": None,
    "profile": None,
    "selected_user_id": 1,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── API helpers ───────────────────────────────────────────────────────────────
def api_get_profile(user_id: int):
    try:
        r = requests.get(f"{API_BASE}/users/{user_id}", timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        st.error(f"Could not reach API: {e}")
    return None

def api_start_session(user_id: int, week: int):
    try:
        r = requests.post(f"{API_BASE}/session/start", json={
            "user_id": user_id,
            "week_number": week,
            "scenario_type": "job interview"
        }, timeout=15)
        if r.status_code == 200:
            return r.json()
        st.error(f"Start session failed: {r.text}")
    except Exception as e:
        st.error(f"Could not reach API: {e}")
    return None

def api_roleplay_turn(user_id: int, message: str):
    try:
        r = requests.post(f"{API_BASE}/session/roleplay", json={
            "user_id": user_id,
            "user_message": message
        }, timeout=30)
        if r.status_code == 200:
            return r.json()
        st.error(f"Roleplay error: {r.text}")
    except Exception as e:
        st.error(f"Could not reach API: {e}")
    return None

def api_end_session(user_id: int, score: float):
    try:
        r = requests.post(f"{API_BASE}/session/end", json={
            "user_id": user_id,
            "score": score
        }, timeout=30)
        if r.status_code == 200:
            return r.json()
        st.error(f"End session error: {r.text}")
    except Exception as e:
        st.error(f"Could not reach API: {e}")
    return None


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="vani-logo">vani.</div>', unsafe_allow_html=True)
    st.markdown('<div class="vani-tagline">AI Communication Coach</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Select Profile</div>', unsafe_allow_html=True)

    user_option = st.selectbox(
        "Profile",
        options=["Priya Sharma — Week 3", "Arjun Mehta — Week 1"],
        label_visibility="collapsed"
    )
    user_id = 1 if "Priya" in user_option else 2

    if user_id != st.session_state.selected_user_id:
        st.session_state.selected_user_id = user_id
        st.session_state.screen = "profile"
        st.session_state.profile = None
        st.session_state.history = []
        st.session_state.session_id = None
        st.session_state.feedback_report = None

    # Load profile
    if st.session_state.profile is None or st.session_state.profile.get("user_name", "").split()[0] != user_option.split()[0]:
        st.session_state.profile = api_get_profile(user_id)

    profile = st.session_state.profile

    if profile:
        st.markdown("<hr class='vani-divider'>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Session Progress</div>', unsafe_allow_html=True)

        avg = profile.get("average_score") or 0
        target = profile.get("target_score") or 100
        pct = min(int((avg / target) * 100), 100)

        st.markdown(f"""
        <div class="score-block">
            <div class="score-number">{avg:.0f}</div>
            <div class="score-label">Current Score</div>
            <div class="score-target">Target: {target:.0f} / 100</div>
            <div class="progress-track">
                <div class="progress-fill" style="width:{pct}%"></div>
            </div>
            <div style="font-size:0.75rem;color:#666;">{pct}% to goal</div>
        </div>
        """, unsafe_allow_html=True)

        delta = profile.get("score_delta") or 0
        week = profile.get("current_week", 1)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<span class="week-badge">Week {week}</span>', unsafe_allow_html=True)
        with col2:
            if delta > 0:
                st.markdown(f'<span class="delta-up">▲ +{delta:.1f}</span>', unsafe_allow_html=True)
            elif delta < 0:
                st.markdown(f'<span class="delta-down">▼ {delta:.1f}</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="week-badge">→ 0.0</span>', unsafe_allow_html=True)

    st.markdown("<hr class='vani-divider'>", unsafe_allow_html=True)

    # Navigation
    if st.session_state.screen != "profile":
        if st.button("← Back to Profile"):
            st.session_state.screen = "profile"
            st.session_state.history = []
            st.session_state.session_id = None
            st.rerun()


# ── Main content ──────────────────────────────────────────────────────────────
profile = st.session_state.profile

# ════════════════════════════════════════════════════════════
# SCREEN 1: PROFILE
# ════════════════════════════════════════════════════════════
if st.session_state.screen == "profile":

    if not profile:
        st.warning("Could not load profile. Is the API running?")
        st.stop()

    col_main, col_side = st.columns([2, 1])

    with col_main:
        st.markdown(f"""
        <div style="margin-bottom:2rem;">
            <div style="font-family:'DM Serif Display',serif;font-size:2.5rem;color:#f0ece4;line-height:1.1;">
                {profile['user_name']}
            </div>
            <div style="color:#666;font-size:0.85rem;margin-top:0.4rem;">
                {profile['onboarding_summary']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-label">Active Behavioral Flags</div>', unsafe_allow_html=True)

        flags = profile.get("behavioral_flags", [])
        if flags:
            for flag in flags:
                st.markdown(f'<div class="flag-card">⚑ {flag}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="flag-card" style="border-left-color:#555;color:#666;">No behavioral flags yet — complete a session first.</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-label">Coaching History</div>', unsafe_allow_html=True)
        summaries = profile.get("past_feedback_summaries", [])
        if summaries:
            for i, s in enumerate(summaries[:3]):
                with st.expander(f"Session {i+1}", expanded=False):
                    st.markdown(f'<div style="font-size:0.875rem;color:#aaa;line-height:1.7;">{s}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:0.875rem;color:#555;">No session history yet.</div>', unsafe_allow_html=True)

    with col_side:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Memory Architecture</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="feedback-block" style="margin-bottom:0.6rem;">
            <div class="feedback-title">🧠 Semantic Memory</div>
            <div class="feedback-text" style="font-size:0.8rem;">ChromaDB — past feedback summaries retrieved via vector similarity</div>
        </div>
        <div class="feedback-block" style="margin-bottom:0.6rem;">
            <div class="feedback-title">📊 Episodic Memory</div>
            <div class="feedback-text" style="font-size:0.8rem;">PostgreSQL — session scores, deltas, behavioral flags, weekly progression</div>
        </div>
        <div class="feedback-block" style="margin-bottom:1.5rem;">
            <div class="feedback-title">💬 Working Memory</div>
            <div class="feedback-text" style="font-size:0.8rem;">In-session conversation buffer — live context window for the roleplay</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Begin Session →", use_container_width=True):
            with st.spinner("Initializing session..."):
                result = api_start_session(user_id, profile["current_week"])
            if result:
                st.session_state.session_id = result["session_id"]
                st.session_state.opening_message = result["opening_message"]
                st.session_state.history = []
                st.session_state.screen = "session"
                st.rerun()


# ════════════════════════════════════════════════════════════
# SCREEN 2: ROLEPLAY SESSION
# ════════════════════════════════════════════════════════════
elif st.session_state.screen == "session":

    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
        <div style="font-family:'DM Serif Display',serif;font-size:1.8rem;color:#f0ece4;">
            Live Session
        </div>
        <div style="color:#666;font-size:0.8rem;margin-top:0.2rem;">
            Session #{st.session_state.session_id} &nbsp;·&nbsp; Adversarial Roleplay Active
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Opening message from Vani
    if st.session_state.opening_message:
        st.markdown(f"""
        <div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:1.25rem 1.5rem;margin-bottom:1.5rem;">
            <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:2px;color:#c9a96e;margin-bottom:0.5rem;">Vani · Coach</div>
            <div style="font-size:0.9rem;color:#ccc;line-height:1.7;white-space:pre-line;">{st.session_state.opening_message}</div>
        </div>
        """, unsafe_allow_html=True)

    # Conversation history
    for turn in st.session_state.history:
        if turn["role"] == "assistant":
            st.markdown(f"""
            <div class="chat-interviewer">
                <div class="chat-role">Interviewer</div>
                {turn['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-user">
                <div class="chat-role">You</div>
                {turn['content']}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Input
    with st.form("chat_form", clear_on_submit=True):
        col_input, col_send = st.columns([5, 1])
        with col_input:
            user_input = st.text_input(
                "Your response",
                placeholder="Type your response here...",
                label_visibility="collapsed"
            )
        with col_send:
            submitted = st.form_submit_button("Send →")

    if submitted and user_input.strip():
        with st.spinner(""):
            result = api_roleplay_turn(user_id, user_input.strip())
        if result:
            st.session_state.history.append({"role": "user", "content": user_input.strip()})
            st.session_state.history.append({"role": "assistant", "content": result["interviewer_response"]})
            st.rerun()

    # End session
    st.markdown("<hr class='vani-divider'>", unsafe_allow_html=True)
    turn_count = len(st.session_state.history) // 2

    col_info, col_end = st.columns([3, 1])
    with col_info:
        st.markdown(f'<div style="color:#555;font-size:0.8rem;padding-top:0.6rem;">{turn_count} exchange{"s" if turn_count != 1 else ""} completed</div>', unsafe_allow_html=True)
    with col_end:
        if turn_count >= 1:
            if st.button("End & Get Feedback", use_container_width=True):
                with st.spinner("Generating feedback report..."):
                    # Auto-score based on turn count as a simple heuristic
                    # In production this would be a real scoring model
                    base_score = (profile.get("average_score") or 60)
                    score = min(base_score + (turn_count * 0.5), 100)
                    result = api_end_session(user_id, round(score, 1))
                if result:
                    st.session_state.feedback_report = result
                    st.session_state.screen = "feedback"
                    st.rerun()


# ════════════════════════════════════════════════════════════
# SCREEN 3: FEEDBACK REPORT
# ════════════════════════════════════════════════════════════
elif st.session_state.screen == "feedback":

    report = st.session_state.feedback_report
    if not report:
        st.error("No feedback found.")
        st.stop()

    score = report.get("score", 0)
    feedback_text = report.get("feedback_report", "")

    st.markdown(f"""
    <div style="margin-bottom:2rem;">
        <div style="font-family:'DM Serif Display',serif;font-size:1.8rem;color:#f0ece4;">
            Session Complete
        </div>
        <div style="color:#666;font-size:0.8rem;margin-top:0.2rem;">
            Session #{report.get('session_id')} &nbsp;·&nbsp; Results saved to memory
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_score, col_report = st.columns([1, 2])

    with col_score:
        avg = profile.get("average_score") or 0
        target = profile.get("target_score") or 100
        gap = target - score

        st.markdown(f"""
        <div class="score-block">
            <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:2px;color:#666;margin-bottom:0.5rem;">Session Score</div>
            <div class="score-number">{score:.1f}</div>
            <div class="score-label">out of 100</div>
            <div class="progress-track">
                <div class="progress-fill" style="width:{min(int(score),100)}%"></div>
            </div>
            <div style="font-size:0.8rem;color:#666;">{gap:.1f} pts to target</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="feedback-block">
            <div class="feedback-title">Stored To Memory</div>
            <div class="feedback-text" style="font-size:0.8rem;">
                ✓ Score written to PostgreSQL<br>
                ✓ Feedback indexed in ChromaDB<br>
                ✓ Available in next session context
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Start New Session", use_container_width=True):
            st.session_state.screen = "profile"
            st.session_state.history = []
            st.session_state.session_id = None
            st.session_state.feedback_report = None
            st.session_state.profile = None
            st.rerun()

    with col_report:
        st.markdown('<div class="section-label">Feedback Report</div>', unsafe_allow_html=True)

        # Parse the 4 sections from the feedback text
        sections = [
            ("1", "OBSERVATION"),
            ("2", "PATTERN"),
            ("3", "IMMEDIATE ACTION"),
            ("4", "BIGGER PICTURE"),
        ]

        raw = feedback_text
        for num, title in sections:
            marker = f"{num}. {title}"
            next_markers = [f"{n}. {t}" for n, t in sections if n != num]

            start = raw.find(marker)
            if start == -1:
                continue
            start += len(marker)

            end = len(raw)
            for nm in next_markers:
                pos = raw.find(nm, start)
                if pos != -1 and pos < end:
                    end = pos

            content = raw[start:end].strip().lstrip("\n").strip("---").strip()

            st.markdown(f"""
            <div class="feedback-block">
                <div class="feedback-number">{num}</div>
                <div class="feedback-title">{title}</div>
                <div class="feedback-text">{content}</div>
            </div>
            """, unsafe_allow_html=True)