from flask import Blueprint, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from datetime import date
from database import db
from models import User, Trek, Booking, Notification, JobExport
from jobs.export_history import generate_history_export
from services.cache import clear_cache

bookings_bp = Blueprint(
    'bookings',
    __name__,
    url_prefix='/api/bookings'
)


@bookings_bp.route('/<int:trek_id>', methods=['POST'])
@jwt_required()
def book_trek(trek_id):

    claims = get_jwt()

    if claims.get('role') != 'trekker':
        return jsonify({
            'message': 'Only trekkers can book a trek'
        }), 403

    user_id = int(get_jwt_identity())

    user = db.session.get(User, user_id)

    if not user or user.is_blacklisted:
        return jsonify({
            'message': 'Your account is not eligible for booking'
        }), 403

    trek = db.session.get(Trek, trek_id)

    if not trek:
        return jsonify({
            'message': 'Trek not found'
        }), 404

    if trek.status != 'Open':
        return jsonify({
            'message': 'This trek is not open for booking'
        }), 400

    if trek.available_slots <= 0:
        return jsonify({
            'message': 'No available slots for this trek'
        }), 400

    existing_booking = db.session.execute(
        db.select(Booking).filter_by(
            user_id=user_id,
            trek_id=trek_id,
            status='Booked'
        )
    ).scalar_one_or_none()

    if existing_booking:
        return jsonify({
            'message': 'You have already booked this trek'
        }), 409

    try:
        # Reduce available slots
        trek.available_slots -= 1

        if trek.available_slots == 0:
            trek.status = 'Full'

        booking = Booking(
            user_id=user_id,
            trek_id=trek_id,
            status='Booked'
        )

        db.session.add(booking)

        # Create booking notification
        notification = Notification(user_id=user_id, message=f"Your booking for {trek.name} has been confirmed.")

        db.session.add(notification)
        db.session.commit()

        clear_cache("admin:dashboard")

        return jsonify({
            'message': 'Trek booked successfully',
            'booking': {
                'booking_id': booking.id,
                'trek_id': trek.id,
                'trek_name': trek.name,
                'booking_status': booking.status,
                'available_slots': trek.available_slots
            }
        }), 201

    except Exception:
        db.session.rollback()

        return jsonify({
            'message': 'Booking failed due to a server error'
        }), 500


@bookings_bp.route('/my-bookings', methods=['GET'])
@jwt_required()
def get_my_bookings():

    claims = get_jwt()

    if claims.get('role') != 'trekker':
        return jsonify({
            'message': 'Only trekkers can access their bookings'
        }), 403

    user_id = int(get_jwt_identity())

    user = db.session.get(User, user_id)

    if not user or user.is_blacklisted:
        return jsonify({
            'message': 'Your account is not eligible to access bookings'
        }), 403

    bookings = db.session.execute(
        db.select(Booking)
        .filter_by(user_id=user_id)
        .order_by(Booking.booking_date.desc())
    ).scalars().all()

    booking_list = []

    for booking in bookings:

        trek = booking.trek

        booking_list.append({
            'booking_id': booking.id,
            'trek_id': booking.trek_id,
            'trek_name': trek.name,
            'location': trek.location,
            'difficulty': trek.difficulty,
            'duration': trek.duration,
            'start_date': trek.start_date.isoformat(),
            'end_date': trek.end_date.isoformat(),
            'booking_date': booking.booking_date.isoformat(),
            'booking_status': booking.status
        })

    return jsonify({
        'message': 'Your bookings fetched successfully',
        'total_bookings': len(booking_list),
        'bookings': booking_list
    }), 200

 
@bookings_bp.route('/<int:booking_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_booking(booking_id):

    claims = get_jwt()

    if claims.get('role') != 'trekker':
        return jsonify({
            'message': 'Only trekkers can cancel bookings'
        }), 403

    user_id = int(get_jwt_identity())

    user = db.session.get(User, user_id)

    if not user or user.is_blacklisted:
        return jsonify({
            'message': 'Your account is not eligible'
        }), 403

    booking = db.session.get(Booking, booking_id)

    if not booking or booking.user_id != user_id:
        return jsonify({
            'message': 'Booking not found'
        }), 404

    if booking.status != 'Booked':
        return jsonify({
            'message': 'This booking cannot be cancelled'
        }), 400

    trek = db.session.get(Trek, booking.trek_id)

    if not trek:
        return jsonify({
            'message': 'Associated trek not found'
        }), 404

    try:
        booking.status = 'Cancelled'

        trek.available_slots += 1

        if trek.status == 'Full':
            trek.status = 'Open'

        # Create cancellation notification
        notification = Notification(user_id=user_id, message=f"Your booking for {booking.trek.name} has been cancelled successfully.")
        db.session.add(notification)    

        db.session.commit()

        clear_cache("admin:dashboard")

        return jsonify({
            'message': 'Booking cancelled successfully',
            'booking_id': booking.id,
            'booking_status': booking.status,
            'available_slots': trek.available_slots
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
            'message': 'Failed to cancel booking'
        }), 500


@bookings_bp.route('/history', methods=['GET'])
@jwt_required()
def get_trekking_history():

    claims = get_jwt()

    if claims.get('role') != 'trekker':
        return jsonify({
            'message': 'Only trekkers can access trekking history'
        }), 403

    user_id = int(get_jwt_identity())

    user = db.session.get(User, user_id)

    if not user or user.is_blacklisted:
        return jsonify({
            'message': 'Your account is not eligible'
        }), 403

    bookings = db.session.execute(
        db.select(Booking)
        .filter_by(user_id=user_id)
        .order_by(Booking.booking_date.desc())
    ).scalars().all()

    history = []

    for booking in bookings:

        trek = booking.trek

        if not trek:
            continue

        # Determine whether the trek has been completed
        if booking.status == 'Cancelled':
            display_status = 'Cancelled'

        elif trek.end_date < date.today():
            display_status = 'Completed'

        else:
            continue

        history.append({
            'booking_id': booking.id,
            'trek_id': trek.id,
            'trek_name': trek.name,
            'location': trek.location,
            'difficulty': trek.difficulty,
            'duration': trek.duration,
            'start_date': trek.start_date.isoformat(),
            'end_date': trek.end_date.isoformat(),
            'booking_date': booking.booking_date.isoformat(),
            'status': display_status
        })

    return jsonify({
        'message': 'Trekking history fetched successfully',
        'total_records': len(history),
        'history': history
    }), 200

@bookings_bp.route('/history/export', methods=['POST'])
@jwt_required()
def request_history_export():

    user_id = get_jwt_identity()

    export = JobExport(
        user_id=int(user_id),
        status="Pending"
    )

    db.session.add(export)
    db.session.commit()

    generate_history_export.delay(export.id)

    return jsonify({
        "message": "Trekking history export request submitted successfully.",
        "export_id": export.id,
        "status": export.status
    }), 202

@bookings_bp.route('/history/export/<int:export_id>', methods=['GET'])
@jwt_required()
def check_history_export(export_id):

    user_id = int(get_jwt_identity())

    export = db.session.execute(
        db.select(JobExport).filter_by(
            id=export_id,
            user_id=user_id
        )
    ).scalar_one_or_none()

    if not export:
        return jsonify({
            "message": "Export request not found."
        }), 404

    return jsonify({
        "export_id": export.id,
        "status": export.status,
        "created_at": export.created_at.isoformat(),
        "download_available": export.status == "Completed"
    }), 200

@bookings_bp.route('/history/export/<int:export_id>/download', methods=['GET'])
@jwt_required()
def download_history_export(export_id):

    user_id = int(get_jwt_identity())

    export = db.session.execute(
        db.select(JobExport).filter_by(
            id=export_id,
            user_id=user_id
        )
    ).scalar_one_or_none()

    if not export:
        return jsonify({
            "message": "Export request not found."
        }), 404

    if export.status != "Completed":
        return jsonify({
            "message": "Export file is not ready yet.",
            "status": export.status
        }), 400

    if not export.file_path:
        return jsonify({
            "message": "Export file path not found."
        }), 404

    try:
        return send_file(
            export.file_path,
            as_attachment=True,
            download_name="trekking_history.csv",
            mimetype="text/csv"
        )

    except (FileNotFoundError, OSError):
        return jsonify({
            "message": "Export file is missing from the server."
        }), 404