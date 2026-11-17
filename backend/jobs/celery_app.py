
import os
import sys

from celery import Celery
from celery.schedules import crontab




BACKEND_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)



celery = Celery(
    'trekking_management',

    broker='redis://localhost:6379/0',

    backend='redis://localhost:6379/0',

    include=[
        'jobs.reminders',
        'jobs.monthly_report',
        'jobs.export_history'
    ]
)




class FlaskContextTask(celery.Task):

    def __call__(self, *args, **kwargs):

        # Ensure backend directory is available
        if BACKEND_DIR not in sys.path:
            sys.path.insert(0, BACKEND_DIR)

        # Import Flask application
        from app import app

        # Execute task inside Flask application context
        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = FlaskContextTask


celery.conf.beat_schedule = {

    # Daily trek reminders at 8:00 AM
    'daily-trek-reminders': {
        'task': 'jobs.reminders.send_trek_reminders',
        'schedule': crontab(
            hour=8,
            minute=0
        ),
    },

    # Monthly booking report on 1st day at 8:00 AM
    'monthly-booking-report': {
        'task': 'jobs.monthly_report.generate_monthly_report',
        'schedule': crontab(
            day_of_month=1,
            hour=8,
            minute=0
        ),
    }

}

celery.conf.timezone = 'Asia/Kolkata'

celery.conf.enable_utc = False
