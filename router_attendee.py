from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from eventdatabase import get_db
import eventmodels
import services
import schemas
from typing import List

router = APIRouter(
    prefix="/attendees",
    tags=["attendees"]
)

@router.post("/{event_id}", response_model=schemas.Attendee)
def register_attendee(event_id: int, attendee: schemas.AttendeeCreate, db: Session = Depends(get_db)):
    return services.register_attendee(db, event_id, attendee)

@router.post("/{attendee_id}/check-in", response_model=schemas.Attendee)
def check_in_attendee(attendee_id: int, db: Session = Depends(get_db)):
    return services.check_in_attendee(db, attendee_id)

@router.get("/{event_id}", response_model=List[schemas.Attendee])
def list_attendees(event_id: int, db: Session = Depends(get_db)):
    return services.list_attendees(db, event_id)