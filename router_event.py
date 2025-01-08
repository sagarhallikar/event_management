from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from eventdatabase import get_db
import eventmodels
import services
import schemas
from typing import List

router = APIRouter(
    prefix="/events",
    tags=["events"]
)

@router.post("/", response_model=schemas.Event)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    return services.create_event(db, event)

@router.put("/{event_id}", response_model=schemas.Event)
def update_event(event_id: int, event: schemas.EventUpdate, db: Session = Depends(get_db)):
    return services.update_event(db, event_id, event)

@router.get("/", response_model=List[schemas.Event])
def list_events(status: str = None, location: str = None, date: str = None, db: Session = Depends(get_db)):
    return services.list_events(db, status, location, date)