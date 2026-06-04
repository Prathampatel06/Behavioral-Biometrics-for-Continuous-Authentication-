from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from backend.database import get_db, BehavioralEvent, AuthenticationLog
from datetime import datetime
from ml_models.typing_rhythm_model import TypingRhythmModel
from ml_models.mouse_movement_model import MouseMovementModel
from ml_models.touchscreen_model import TouchscreenModel
from ml_models.ensemble_model import EnsembleModel

router = APIRouter()


class EventPayload(BaseModel):
    user_id: int
    events: List[dict]
    metadata: Optional[dict] = None


typing_model = TypingRhythmModel()
mouse_model = MouseMovementModel()
touch_model = TouchscreenModel()
ensemble = EnsembleModel()


def _save_event(db: Session, user_id: int, event_type: str, features: dict, confidence: float, verified: Optional[bool]):
    ev = BehavioralEvent(
        user_id=user_id,
        event_type=event_type,
        features=features,
        confidence_score=confidence,
        is_verified=verified,
        created_at=datetime.utcnow()
    )
    db.add(ev)
    db.flush()
    return ev


def _save_auth_log(db: Session, user_id: int, status: str, confidence: float, method: str):
    log = AuthenticationLog(
        user_id=user_id,
        status=status,
        confidence_score=confidence,
        method=method,
        created_at=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    return log


@router.post("/typing")
async def verify_typing(payload: EventPayload, db: Session = Depends(get_db)):
    """Verify typing pattern"""
    if not payload.events:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No events provided")

    pred = typing_model.predict(payload.events)
    confidence = pred.get('confidence', 0.0)
    is_auth = pred.get('is_authentic', False)

    _save_event(db, payload.user_id, 'keystroke', {'events': payload.events}, confidence, is_auth)
    status_str = 'success' if is_auth else 'failed'
    _save_auth_log(db, payload.user_id, status_str, confidence, 'typing')

    return {
        'model': 'typing_rhythm',
        'confidence': confidence,
        'is_authentic': is_auth
    }


@router.post("/mouse")
async def verify_mouse(payload: EventPayload, db: Session = Depends(get_db)):
    """Verify mouse movement pattern"""
    if not payload.events:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No events provided")

    pred = mouse_model.predict(payload.events)
    confidence = pred.get('confidence', 0.0)
    is_auth = pred.get('is_authentic', False)

    _save_event(db, payload.user_id, 'mouse_move', {'events': payload.events}, confidence, is_auth)
    status_str = 'success' if is_auth else 'failed'
    _save_auth_log(db, payload.user_id, status_str, confidence, 'mouse')

    return {
        'model': 'mouse_movement',
        'confidence': confidence,
        'is_authentic': is_auth
    }


@router.post("/touch")
async def verify_touch(payload: EventPayload, db: Session = Depends(get_db)):
    """Verify touchscreen pattern"""
    if not payload.events:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No events provided")

    pred = touch_model.predict(payload.events)
    confidence = pred.get('confidence', 0.0)
    is_auth = pred.get('is_authentic', False)

    _save_event(db, payload.user_id, 'touch', {'events': payload.events}, confidence, is_auth)
    status_str = 'success' if is_auth else 'failed'
    _save_auth_log(db, payload.user_id, status_str, confidence, 'touch')

    return {
        'model': 'touchscreen',
        'confidence': confidence,
        'is_authentic': is_auth
    }


class EnsemblePayload(BaseModel):
    user_id: int
    keystroke_events: Optional[List[dict]] = None
    mouse_events: Optional[List[dict]] = None
    touch_events: Optional[List[dict]] = None


@router.post("/ensemble")
async def verify_ensemble(payload: EnsemblePayload, db: Session = Depends(get_db)):
    """Verify using ensemble of models"""
    pred = ensemble.predict(
        keystroke_events=payload.keystroke_events,
        mouse_events=payload.mouse_events,
        touch_events=payload.touch_events
    )

    confidence = pred.get('ensemble_confidence', 0.0)
    is_auth = pred.get('is_authentic', False)

    # Store a combined event
    _save_event(db, payload.user_id, 'ensemble', {
        'typing': pred.get('model_predictions', {}).get('typing'),
        'mouse': pred.get('model_predictions', {}).get('mouse'),
        'touch': pred.get('model_predictions', {}).get('touch')
    }, confidence, is_auth)

    status_str = 'success' if is_auth else 'failed'
    _save_auth_log(db, payload.user_id, status_str, confidence, 'ensemble')

    return {
        'model': 'ensemble',
        'confidence': confidence,
        'is_authentic': is_auth,
        'threshold': pred.get('threshold')
    }
