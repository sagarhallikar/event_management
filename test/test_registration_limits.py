import pytest
from fastapi.testclient import TestClient
from main import app, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from eventdatabase import Base
import eventmodels

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

def test_registration_limits(client):
    # Create an event with a max_attendees limit of 2
    response = client.post("/events/", json={
        "name": "Test Event",
        "description": "Test Description",
        "start_time": "2025-01-01T10:00:00",
        "end_time": "2025-01-01T12:00:00",
        "location": "Test Location",
        "max_attendees": 3,
        "status": "scheduled"
    })
    assert response.status_code == 200
    event_id = response.json()["event_id"]

    # Register three attendees with unique email addresses
    for i in range(3):
        response = client.post(f"/events/{event_id}/attendees/", json={
            "first_name": f"Attendee{i+1}",
            "last_name": "Test",
            "email": f"attendee{i+1}@test.com",
            "phone_number": "1234567890"
        })
        assert response.status_code == 200

    # Try to register a third attendee, which should fail
    response = client.post(f"/events/{event_id}/attendees/", json={
        "first_name": "Attendee3",
        "last_name": "Test",
        "email": "attendee3@test.com",
        "phone_number": "1234567890"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Event is full"