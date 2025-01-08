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

def test_check_ins(client):
    # Create an event
    response = client.post("/events/", json={
        "name": "Test Event",
        "description": "Test Description",
        "start_time": "2025-01-01T10:00:00",
        "end_time": "2025-01-01T12:00:00",
        "location": "Test Location",
        "max_attendees": 2,
        "status": "scheduled"
    })
    assert response.status_code == 200
    event_id = response.json()["event_id"]

    # Register an attendee
    response = client.post(f"/events/{event_id}/attendees/", json={
        "first_name": "Attendee1",
        "last_name": "Test",
        "email": "attendee1@test.com",
        "phone_number": "1234567890"
    })
    assert response.status_code == 200
    attendee_id = response.json()["attendee_id"]

    # Check-in the attendee
    response = client.post(f"/attendees/{attendee_id}/check-in")
    assert response.status_code == 200
    assert response.json()["check_in_status"] == True