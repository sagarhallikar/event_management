from sqlalchemy.orm import Session
import eventmodels
import schemas
from fastapi import HTTPException

def create_event(db: Session, event: schemas.EventCreate):
    db_event = eventmodels.Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def update_event(db: Session, event_id: int, event: schemas.EventUpdate):
    db_event = db.query(eventmodels.Event).filter(eventmodels.Event.event_id == event_id).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    for key, value in event.model_dump().items():
        setattr(db_event, key, value)
    db.commit()
    db.refresh(db_event)
    return db_event

def register_attendee(db: Session, event_id: int, attendee: schemas.AttendeeCreate):
    event = db.query(eventmodels.Event).filter(eventmodels.Event.event_id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    if len(event.attendees) >= event.max_attendees:
        raise HTTPException(status_code=400, detail="Event is full")
    db_attendee = eventmodels.Attendee(**attendee.model_dump(), event_id=event_id)
    db.add(db_attendee)
    db.commit()
    db.refresh(db_attendee)
    return db_attendee

def check_in_attendee(db: Session, attendee_id: int):
    attendee = db.query(eventmodels.Attendee).filter(eventmodels.Attendee.attendee_id == attendee_id).first()
    if attendee is None:
        raise HTTPException(status_code=404, detail="Attendee not found")
    attendee.check_in_status = True
    db.commit()
    db.refresh(attendee)
    return attendee

def list_events(db: Session, status: str = None, location: str = None, date: str = None):
    query = db.query(eventmodels.Event)
    if status:
        query = query.filter(eventmodels.Event.status == status)
    if location:
        query = query.filter(eventmodels.Event.location == location)
    if date:
        query = query.filter(eventmodels.Event.start_time <= date, eventmodels.Event.end_time >= date)
    return query.all()

def list_attendees(db: Session, event_id: int):
    event = db.query(eventmodels.Event).filter(eventmodels.Event.event_id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event.attendees