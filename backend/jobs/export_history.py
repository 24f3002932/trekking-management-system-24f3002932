from jobs.celery_app import celery
from database import db
from models import JobExport, Booking, Trek
from datetime import date
import csv


@celery.task
def generate_history_export(export_id):

    export = db.session.get(JobExport, export_id)

    if not export:
        return "Export request not found."

    try:
        export.status = "Processing"
        db.session.commit()

        file_path = f"exports/trek_history_{export.user_id}_{export.id}.csv"

        bookings = db.session.execute(
            db.select(Booking, Trek)
            .join(Trek, Booking.trek_id == Trek.id)
            .filter(Booking.user_id == export.user_id)
        ).all()

        with open(file_path, "w", newline="", encoding="utf-8") as file:

            writer = csv.writer(file)

            writer.writerow([
                "Booking ID",
                "Trek Name",
                "Location",
                "Difficulty",
                "Start Date",
                "End Date",
                "Booking Date",
                "Status"
            ])

            for booking, trek in bookings:

                if booking.status == "Cancelled":
                    history_status = "Cancelled"

                elif trek.end_date < date.today():
                    history_status = "Completed"

                else:
                    continue

                writer.writerow([
                    booking.id,
                    trek.name,
                    trek.location,
                    trek.difficulty,
                    trek.start_date,
                    trek.end_date,
                    booking.booking_date,
                    history_status
                ])

        export.file_path = file_path
        export.status = "Completed"
        db.session.commit()

        return f"Export {export.id} completed successfully."

    except Exception as error:

        export.status = "Failed"
        db.session.commit()

        return f"Export failed: {str(error)}"