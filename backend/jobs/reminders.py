from jobs.celery_app import celery
from database import db
from models import Booking, Notification, Trek
from datetime import date, timedelta


@celery.task
def send_trek_reminders():

    # Get tomorrow's date
    tomorrow = date.today() + timedelta(days=1)

    # Find all active bookings for tomorrow's treks
    bookings = db.session.execute(db.select(Booking).join(Trek, Booking.trek_id == Trek.id).filter(
        Booking.status == 'Booked',
        Trek.start_date == tomorrow
    )).scalars().all()

    reminder_count = 0

    for booking in bookings:

        trek = booking.trek

        message = (
            f"Reminder: Your trek {trek.name} "
            f"starts tomorrow ({tomorrow})."
        )

        # Prevent duplicate reminder notifications
        existing_notification = db.session.execute(
            db.select(Notification).filter_by(
                user_id=booking.user_id,
                message=message
            )
        ).scalar_one_or_none()

        if existing_notification:
            continue

        notification = Notification(
            user_id=booking.user_id,
            message=message
        )

        db.session.add(notification)
        reminder_count += 1

    db.session.commit()

    return f"{reminder_count} trek reminders created."