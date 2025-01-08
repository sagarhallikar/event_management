from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import enum
import pytz

IST = pytz.timezone('Asia/Kolkata')

class EventStatus(str, enum.Enum):
    scheduled = "scheduled"
    ongoing = "ongoing"
    completed = "completed"
    canceled = "canceled"

class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: str
    max_attendees: int
    status: EventStatus = EventStatus.scheduled

    class Config:
        json_encoders = {
            datetime: lambda v: v.astimezone(IST).isoformat()
        }

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    pass

class Event(EventBase):
    event_id: int

    class Config:
        from_attributes = True

class AttendeeBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str

class AttendeeCreate(AttendeeBase):
    pass

class Attendee(AttendeeBase):
    attendee_id: int
    event_id: int
    check_in_status: bool

    class Config:
        from_attributes = True