import pytest
from fastapi.testclient import TestClient
from main import app, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from eventdatabase import Base
import eventmodels
import event_tasks
from datetime import datetime, timedelta
import pytz

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

def test_status_updates(client):
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)

    # Create an event that is currently ongoing
    response = client.post("/events/", json={
        "name": "Ongoing Event",
        "description": "Test Description",
        "start_time": (current_time - timedelta(hours=1)).isoformat(),
        "end_time": (current_time + timedelta(hours=1)).isoformat(),
        "location": "Test Location",
        "max_attendees": 2,
        "status": "scheduled"
    })
    assert response.status_code == 200
    event_id = response.json()["event_id"]

    # Run the status update task
    db = TestingSessionLocal()
    event_tasks.update_event_statuses(db)
    db.close()

    # Check if the event status is updated to 'ongoing'
    response = client.get(f"/events/")
    events = response.json()
    for event in events:
        if event["event_id"] == event_id:
            assert event["status"] == "ongoing"

    # Create an event that has ended
    response = client.post("/events/", json={
        "name": "Completed Event",
        "description": "Test Description",
        "start_time": (current_time - timedelta(hours=2)).isoformat(),
        "end_time": (current_time - timedelta(hours=1)).isoformat(),
        "location": "Test Location",
        "max_attendees": 2,
        "status": "scheduled"
    })
    assert response.status_code == 200
    event_id = response.json()["event_id"]

    # Run the status update task
    db = TestingSessionLocal()
    event_tasks.update_event_statuses(db)
    db.close()

    # Check if the event status is updated to 'completed'
    response = client.get(f"/events/")
    events = response.json()
    for event in events:
        if event["event_id"] == event_id:
            assert event["status"] == "completed"