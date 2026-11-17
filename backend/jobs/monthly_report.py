from jobs.celery_app import celery
from database import db
from models import Booking, Trek, User, Notification
from datetime import date, datetime


@celery.task
def generate_monthly_report():

    # Get current month
    today = date.today()

    current_month_start = date(
        today.year, today.month, 1
    )

    # Calculate previous month
    if today.month == 1:
        previous_month = 12
        previous_year = today.year - 1
    else:
        previous_month = today.month - 1
        previous_year = today.year

    previous_month_start = date(
        previous_year, previous_month, 1
    )

    # Count bookings in previous month
    total_bookings = db.session.execute(
        db.select(db.func.count(Booking.id)).filter(
            Booking.booking_date >= datetime.combine(
                previous_month_start, datetime.min.time()
            ),
            Booking.booking_date < datetime.combine(
                current_month_start, datetime.min.time()
            )
        )
    ).scalar_one()

    # Count confirmed bookings
    confirmed_bookings = db.session.execute(
        db.select(db.func.count(Booking.id)).filter(
            Booking.booking_date >= datetime.combine(
                previous_month_start, datetime.min.time()
            ),
            Booking.booking_date < datetime.combine(
                current_month_start, datetime.min.time()
            ),
            Booking.status == 'Booked'
        )
    ).scalar_one()

    # Count cancelled bookings
    cancelled_bookings = db.session.execute(
        db.select(db.func.count(Booking.id)).filter(
            Booking.booking_date >= datetime.combine(
                previous_month_start, datetime.min.time()
            ),
            Booking.booking_date < datetime.combine(
                current_month_start, datetime.min.time()
            ),
            Booking.status == 'Cancelled'
        )
    ).scalar_one()

    # Prepare report message
    message = (
        f"Monthly Report - {previous_month}/{previous_year}. "
        f"Total Bookings: {total_bookings}, "
        f"Confirmed: {confirmed_bookings}, "
        f"Cancelled: {cancelled_bookings}."
    )

    # Notify all admins
    admins = db.session.execute(
        db.select(User).filter_by(role='admin')
    ).scalars().all()

    for admin in admins:

        notification = Notification(
            user_id=admin.id,
            message=message
        )

        db.session.add(notification)

    db.session.commit()

    return message