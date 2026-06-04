from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from backend.config import settings

# Database URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {},
    pool_pre_ping=True,
    pool_recycle=3600
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Database session dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

class BiometricProfile(Base):
    __tablename__ = "biometric_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    profile_type = Column(String, nullable=False)  # typing, mouse, touch
    model_path = Column(String, nullable=True)
    enrollment_samples = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class BehavioralEvent(Base):
    __tablename__ = "behavioral_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    event_type = Column(String, nullable=False)  # keystroke, mouse_move, touch
    features = Column(JSON, nullable=False)
    confidence_score = Column(Float, nullable=True)
    is_verified = Column(Boolean, default=None)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuthenticationLog(Base):
    __tablename__ = "authentication_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    status = Column(String, nullable=False)  # success, failed, suspicious
    confidence_score = Column(Float, nullable=False)
    method = Column(String, nullable=False)  # typing, mouse, touch, ensemble
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class EnrollmentSession(Base):
    __tablename__ = "enrollment_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    session_token = Column(String, unique=True, index=True)
    status = Column(String, default="active")  # active, completed, cancelled
    samples_collected = Column(Integer, default=0)
    target_samples = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
