from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from eventdatabase import SessionLocal, engine
import eventmodels
import schemas
from event_tasks import start_scheduler
from typing import List

eventmodels.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Start the scheduler
start_scheduler()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/events/", response_model=schemas.Event)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    db_event = eventmodels.Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.put("/events/{event_id}", response_model=schemas.Event)
def update_event(event_id: int, event: schemas.EventUpdate, db: Session = Depends(get_db)):
    db_event = db.query(eventmodels.Event).filter(eventmodels.Event.event_id == event_id).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    for key, value in event.model_dump().items():
        setattr(db_event, key, value)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.post("/events/{event_id}/attendees/", response_model=schemas.Attendee)
def register_attendee(event_id: int, attendee: schemas.AttendeeCreate, db: Session = Depends(get_db)):
    event = db.query(eventmodels.Event).filter(eventmodels.Event.event_id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    if len(event.attendees) >= event.max_attendees:
        raise HTTPException(status_code=400, detail="Event is full")
    existing_attendee = db.query(eventmodels.Attendee).filter(eventmodels.Attendee.email == attendee.email).first()
    if existing_attendee:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_attendee = eventmodels.Attendee(**attendee.model_dump(), event_id=event_id)
    db.add(db_attendee)
    db.commit()
    db.refresh(db_attendee)
    return db_attendee

@app.post("/attendees/{attendee_id}/check-in", response_model=schemas.Attendee)
def check_in_attendee(attendee_id: int, db: Session = Depends(get_db)):
    attendee = db.query(eventmodels.Attendee).filter(eventmodels.Attendee.attendee_id == attendee_id).first()
    if attendee is None:
        raise HTTPException(status_code=404, detail="Attendee not found")
    attendee.check_in_status = True
    db.commit()
    db.refresh(attendee)
    return attendee

@app.get("/events/", response_model=List[schemas.Event])
def list_events(status: str = None, location: str = None, date: str = None, db: Session = Depends(get_db)):
    query = db.query(eventmodels.Event)
    if status:
        query = query.filter(eventmodels.Event.status == status)
    if location:
        query = query.filter(eventmodels.Event.location == location)
    if date:
        query = query.filter(eventmodels.Event.start_time <= date, eventmodels.Event.end_time >= date)
    return query.all()

@app.get("/events/{event_id}/attendees/", response_model=List[schemas.Attendee])
def list_attendees(event_id: int, db: Session = Depends(get_db)):
    event = db.query(eventmodels.Event).filter(eventmodels.Event.event_id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event.attendees