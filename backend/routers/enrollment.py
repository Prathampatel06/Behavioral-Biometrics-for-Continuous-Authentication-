from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import uuid
from backend.database import get_db, EnrollmentSession, User, BehavioralEvent
from ml_models.train import train_models_from_enrollment

router = APIRouter()

class EnrollmentStartRequest(BaseModel):
    user_id: int

class EnrollmentStartResponse(BaseModel):
    session_id: int
    session_token: str
    target_samples: int
    message: str

class BiometricDataCapture(BaseModel):
    user_id: int
    event_type: str  # keystroke, mouse_move, touch
    features: dict
    session_token: str

class EnrollmentCompleteRequest(BaseModel):
    session_token: str
    user_id: int

@router.post("/start", response_model=EnrollmentStartResponse)
async def start_enrollment(
    request: EnrollmentStartRequest,
    db: Session = Depends(get_db)
):
    """Start a new enrollment session"""
    # Verify user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create enrollment session
    session_token = str(uuid.uuid4())
    enrollment_session = EnrollmentSession(
        user_id=request.user_id,
        session_token=session_token,
        target_samples=100
    )
    db.add(enrollment_session)
    db.commit()
    db.refresh(enrollment_session)
    
    return {
        "session_id": enrollment_session.id,
        "session_token": session_token,
        "target_samples": enrollment_session.target_samples,
        "message": "Enrollment session started. Start typing/moving mouse/using touch."
    }

@router.post("/capture")
async def capture_biometric_data(
    data: BiometricDataCapture,
    db: Session = Depends(get_db)
):
    """Capture biometric data during enrollment"""
    # Verify enrollment session exists and is active
    session = db.query(EnrollmentSession).filter(
        EnrollmentSession.session_token == data.session_token,
        EnrollmentSession.user_id == data.user_id,
        EnrollmentSession.status == "active"
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or inactive enrollment session"
        )
    
    # Store behavioral event
    event = BehavioralEvent(
        user_id=data.user_id,
        event_type=data.event_type,
        features=data.features,
        is_verified=None
    )
    db.add(event)
    
    # Update session sample count
    session.samples_collected += 1
    
    # Check if enrollment is complete
    if session.samples_collected >= session.target_samples:
        session.status = "completed"
        session.completed_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "status": "captured",
        "samples_collected": session.samples_collected,
        "remaining_samples": max(0, session.target_samples - session.samples_collected),
        "enrollment_complete": session.status == "completed"
    }

@router.post("/complete")
async def complete_enrollment(
    request: EnrollmentCompleteRequest,
    db: Session = Depends(get_db)
):
    """Complete enrollment and train models"""
    # Verify session
    session = db.query(EnrollmentSession).filter(
        EnrollmentSession.session_token == request.session_token,
        EnrollmentSession.user_id == request.user_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment session not found"
        )
    
    if session.status != "completed" and session.samples_collected < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient samples. Collected: {session.samples_collected}, Required: 50"
        )

    # If the session is still active and enough samples were collected, mark it complete.
    if session.status != "completed":
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(session)

    # Collect all enrollment events for this session window.
    query = db.query(BehavioralEvent).filter(
        BehavioralEvent.user_id == request.user_id,
        BehavioralEvent.created_at >= session.created_at
    )
    if session.completed_at:
        query = query.filter(BehavioralEvent.created_at <= session.completed_at)
    enrollment_events = query.all()

    if not enrollment_events:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No enrollment events found for this session"
        )

    try:
        models_trained = train_models_from_enrollment(enrollment_events)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model training failed: {exc}"
        )

    if not models_trained:
        return {
            "status": "warning",
            "message": "Enrollment completed, but no model had enough event samples to train.",
            "samples_processed": session.samples_collected,
            "models_trained": []
        }

    return {
        "status": "success",
        "message": "Enrollment completed successfully",
        "samples_processed": session.samples_collected,
        "models_trained": models_trained
    }

@router.get("/status/{session_token}")
async def get_enrollment_status(
    session_token: str,
    db: Session = Depends(get_db)
):
    """Get current enrollment session status"""
    session = db.query(EnrollmentSession).filter(
        EnrollmentSession.session_token == session_token
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return {
        "status": session.status,
        "samples_collected": session.samples_collected,
        "target_samples": session.target_samples,
        "progress_percent": int((session.samples_collected / session.target_samples) * 100),
        "enrollment_complete": session.status == "completed"
    }
