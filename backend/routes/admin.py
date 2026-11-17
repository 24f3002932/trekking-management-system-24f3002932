from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import or_
from database import db
from models import User, Trek, Booking, Notification
from services.cache import clear_cache, get_cache, set_cache

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():

    claims = get_jwt()

    if claims.get('role') != 'admin':
        return jsonify({
            'message': 'Access denied. Admin privileges required.'
        }), 403

    # Check Redis cache
    cache_key = "admin:dashboard"

    cached_data = get_cache(cache_key)

    if cached_data is not None:
        print("REDIS CACHE HIT: Dashboard fetched from Redis")
        return jsonify(cached_data), 200
    print("REDIS CACHE MISS: Fetching dashboard from database")

    # Fetch statistics from database
    total_users = db.session.query(User).count()

    total_treks = db.session.query(Trek).count()

    total_bookings = db.session.query(Booking).count()

    total_staff = db.session.query(User).filter_by(
        role='staff'
    ).count()

    response_data = {
        'message': 'Admin dashboard data fetched successfully',
        'statistics': {
            'total_users': total_users,
            'total_treks': total_treks,
            'total_bookings': total_bookings,
            'total_staff': total_staff
        }
    }

    # Store dashboard data for 5 minutes
    set_cache(cache_key, response_data, expiry=300)

    return jsonify(response_data), 200

@admin_bp.route('/bookings', methods=['GET'])
@jwt_required()
def get_all_bookings():

    # Check admin role
    claims = get_jwt()

    if claims.get('role') != 'admin':
        return jsonify({
            'message': 'Access denied. Admin only.'
        }), 403

    # Search by user name or trek name
    search = request.args.get('search', '').strip()

    query = (
        db.select(Booking)
        .join(User, Booking.user_id == User.id)
        .join(Trek, Booking.trek_id == Trek.id)
    )

    if search:
        query = query.filter(
            or_(
                User.name.ilike(f'%{search}%'),
                Trek.name.ilike(f'%{search}%')
            )
        )

    bookings = db.session.execute(
        query.order_by(Booking.booking_date.desc())
    ).scalars().all()

    booking_list = []

    for booking in bookings:

        booking_list.append({
            'booking_id': booking.id,
            'user': {
                'user_id': booking.user.id,
                'name': booking.user.name,
                'email': booking.user.email
            },
            'trek': {
                'trek_id': booking.trek.id,
                'name': booking.trek.name,
                'location': booking.trek.location
            },
            'booking_date': booking.booking_date.isoformat(),
            'status': booking.status
        })

    return jsonify({
        'message': 'Bookings fetched successfully.',
        'total_bookings': len(booking_list),
        'bookings': booking_list
    }), 200

@admin_bp.route('/bookings/<int:booking_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_booking_by_admin(booking_id):

    # Check admin role
    claims = get_jwt()

    if claims.get('role') != 'admin':
        return jsonify({
            'message': 'Access denied. Admin only.'
        }), 403

    # Find booking
    booking = db.session.get(Booking, booking_id)

    if not booking:
        return jsonify({
            'message': 'Booking not found.'
        }), 404

    # Check booking status
    if booking.status != 'Booked':
        return jsonify({
            'message': 'Only active bookings can be cancelled.'
        }), 400

    # Cancel booking
    booking.status = 'Cancelled'

    # Restore available slot
    trek = db.session.get(Trek, booking.trek_id)

    if trek:
        trek.available_slots += 1

        # Reopen trek only if it was Full
        if trek.status == 'Full':
            trek.status = 'Open'

        # Create cancellation notification
        notification = Notification(user_id=booking.user_id,message=f"Your booking for {trek.name} has been cancelled by the admin.")
        db.session.add(notification)
        db.session.commit()

        clear_cache("admin:dashboard")

    return jsonify({
        'message': 'Booking cancelled successfully by admin.',
        'booking_id': booking.id,
        'booking_status': booking.status,
        'available_slots': trek.available_slots if trek else None
    }), 200
