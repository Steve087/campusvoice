from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("Session", back_populates="created_by_user")


class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    total_rows = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    created_by_user = relationship("User", back_populates="sessions")
    feedback_items = relationship("FeedbackItem", back_populates="session")
    analysis_result = relationship("AnalysisResult", back_populates="session", uselist=False)


class FeedbackItem(Base):
    __tablename__ = "feedback_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer)
    session_id = Column(String, ForeignKey("sessions.session_id"))
    text = Column(Text, nullable=False)
    department = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="feedback_items")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.session_id"), unique=True)
    clusters_json = Column(Text)
    department_sentiments_json = Column(Text)
    urgent_items_json = Column(Text)
    noise_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="analysis_result")