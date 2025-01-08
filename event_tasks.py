from datetime import datetime
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from eventdatabase import SessionLocal
import eventmodels
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_event_statuses(db: Session):
    current_time = datetime.utcnow()
    logger.info(f"Current UTC time: {current_time}")

    # Update events to 'ongoing' if the current time is within the event duration
    ongoing_events = db.query(eventmodels.Event).filter(
        eventmodels.Event.start_time <= current_time,
        eventmodels.Event.end_time > current_time,
        eventmodels.Event.status == eventmodels.EventStatus.scheduled
    ).update({eventmodels.Event.status: eventmodels.EventStatus.ongoing}, synchronize_session=False)
    logger.info(f"Updated {ongoing_events} events to 'ongoing'")

    # Update events to 'completed' if the current time is past the end time
    completed_events = db.query(eventmodels.Event).filter(
        eventmodels.Event.end_time <= current_time,
        eventmodels.Event.status.in_([eventmodels.EventStatus.scheduled, eventmodels.EventStatus.ongoing])
    ).update({eventmodels.Event.status: eventmodels.EventStatus.completed}, synchronize_session=False)
    logger.info(f"Updated {completed_events} events to 'completed'")

    db.commit()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: update_event_statuses(SessionLocal()), 'interval', minutes=1)
    scheduler.start()