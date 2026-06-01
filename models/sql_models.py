# models/sql_models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.sql_db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    target_score = Column(Float, nullable=False)          # e.g. 85.0 out of 100
    current_week = Column(Integer, default=1)             # 1 to 10
    onboarding_summary = Column(Text, nullable=True)      # Free text from onboarding
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sessions = relationship("Session", back_populates="user")
    behavioral_flags = relationship("BehavioralFlag", back_populates="user")

    def __repr__(self):
        return f"<User id={self.id} name={self.name} week={self.current_week}>"


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_number = Column(Integer, nullable=False)
    score = Column(Float, nullable=True)                  # Score out of 100 for this session
    scenario_type = Column(String(100), nullable=True)    # e.g. "job interview", "sales pitch"
    feedback_summary = Column(Text, nullable=True)        # AI-generated post-session summary
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<Session id={self.id} user_id={self.user_id} week={self.week_number} score={self.score}>"


class BehavioralFlag(Base):
    __tablename__ = "behavioral_flags"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    flag_text = Column(Text, nullable=False)              # e.g. "speaks too fast when nervous"
    week_identified = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="behavioral_flags")

    def __repr__(self):
        return f"<BehavioralFlag user_id={self.user_id} flag={self.flag_text[:40]}>"
