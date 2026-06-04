import os
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import Base, engine, SessionLocal, User
from backend.auth import get_password_hash

client = TestClient(app)


def setup_module(module):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        user = db.query(User).filter(User.username == "testuser").first()
        if not user:
            user = User(
                username="testuser",
                email="testuser@example.com",
                hashed_password=get_password_hash("TestPassword123")
            )
            db.add(user)
            db.commit()


def test_root_health():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"


def test_register_and_login():
    username = "newuser"
    email = "newuser@example.com"
    password = "NewPassword123"

    # Clean up any existing user
    with SessionLocal() as db:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            db.delete(existing)
            db.commit()

    response = client.post("/api/users/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == username
    assert data["email"] == email

    response = client.post("/api/users/login", json={
        "username": username,
        "password": password
    })
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["user_id"] > 0


def test_enrollment_start():
    with SessionLocal() as db:
        user = db.query(User).filter(User.username == "testuser").first()
        assert user is not None
        user_id = user.id

    response = client.post("/api/enrollment/start", json={"user_id": user_id})
    assert response.status_code == 200
    data = response.json()
    assert "session_token" in data
    assert data["target_samples"] == 100


def test_enrollment_complete_triggers_training():
    with SessionLocal() as db:
        user = db.query(User).filter(User.username == "testuser").first()
        assert user is not None
        user_id = user.id

    start_response = client.post("/api/enrollment/start", json={"user_id": user_id})
    assert start_response.status_code == 200
    session_data = start_response.json()
    session_token = session_data["session_token"]

    # Insert captured enrollment events for each biometric modality.
    with SessionLocal() as db:
        from backend.database import EnrollmentSession, BehavioralEvent

        session = db.query(EnrollmentSession).filter(
            EnrollmentSession.session_token == session_token,
            EnrollmentSession.user_id == user_id
        ).first()
        assert session is not None

        for _ in range(10):
            db.add(BehavioralEvent(
                user_id=user_id,
                event_type="keystroke",
                features={
                    "dwell_times": [120, 130, 110, 125, 140],
                    "flight_times": [80, 75, 90, 85],
                    "key_pressures": [0.5, 0.6, 0.55, 0.45, 0.5],
                    "timestamps": [0, 120, 250, 390, 520]
                },
                is_verified=None
            ))
            db.add(BehavioralEvent(
                user_id=user_id,
                event_type="mouse_move",
                features={
                    "positions": [[0, 0], [10, 5], [20, 12], [26, 18], [30, 25]],
                    "timestamps": [0, 0.1, 0.2, 0.35, 0.5]
                },
                is_verified=None
            ))
            db.add(BehavioralEvent(
                user_id=user_id,
                event_type="touch",
                features={
                    "pressures": [0.3, 0.4, 0.45, 0.35],
                    "areas": [20, 22, 19, 21],
                    "positions": [[0, 0], [5, 2], [10, 8], [14, 12]],
                    "timestamps": [0, 0.08, 0.18, 0.28]
                },
                is_verified=None
            ))

        session.samples_collected = 50
        session.status = "active"
        db.commit()

    complete_response = client.post("/api/enrollment/complete", json={
        "session_token": session_token,
        "user_id": user_id
    })
    assert complete_response.status_code == 200
    complete_data = complete_response.json()
    assert complete_data["status"] == "success"
    assert set(complete_data["models_trained"]) == {"typing_rhythm", "mouse_movement", "touchscreen"}
