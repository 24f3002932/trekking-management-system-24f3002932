from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime

from database import db
from models import Trek, Booking, User, TrekStaff
from services.cache import get_cache, set_cache, clear_cache

trek_bp = Blueprint('treks', __name__, url_prefix='/api/treks')


@trek_bp.route('/', methods=['POST'])
@jwt_required()
def create_trek():

    claims = get_jwt()

    if claims.get('role') != 'admin':
        return jsonify({
            'message': 'Access denied. Admin privileges required.'
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            'message': 'Request body must contain JSON data'
        }), 400

    required_fields = [
        'name', 'location', 'difficulty',
        'duration', 'available_slots',
        'start_date', 'end_date'
    ]

    for field in required_fields:
        if field not in data or data[field] in (None, ''):
            return jsonify({
                'message': field + ' is required'
            }), 400

    try:
        start_date = datetime.strptime(
            data['start_date'], '%Y-%m-%d'
        ).date()

        end_date = datetime.strptime(
            data['end_date'], '%Y-%m-%d'
        ).date()

        duration = int(data['duration'])
        available_slots = int(data['available_slots'])

    except (ValueError, TypeError):
        return jsonify({
            'message': 'Invalid date, duration or available slots'
        }), 400

    if end_date < start_date:
        return jsonify({
            'message': 'End date cannot be before start date'
        }), 400

    if duration <= 0 or available_slots < 0:
        return jsonify({
            'message': 'Duration must be positive and slots cannot be negative'
        }), 400

    difficulty = data['difficulty'].strip().capitalize()

    if difficulty not in ['Easy', 'Moderate', 'Hard']:
        return jsonify({
            'message': 'Difficulty must be Easy, Moderate or Hard'
        }), 400

    trek = Trek(
        name=data['name'].strip(),
        location=data['location'].strip(),
        description=data.get('description', '').strip(),
        difficulty=difficulty,
        duration=duration,
        available_slots=available_slots,
        start_date=start_date,
        end_date=end_date,
        status='Open' if available_slots > 0 else 'Full'
    )

    try:
        db.session.add(trek)
        db.session.commit()

        clear_cache() 

        return jsonify({
            'message': 'Trek created successfully',
            'trek': {
                'id': trek.id,
                'name': trek.name,
                'location': trek.location,
                'difficulty': trek.difficulty,
                'duration': trek.duration,
                'available_slots': trek.available_slots,
                'start_date': trek.start_date.isoformat(),
                'end_date': trek.end_date.isoformat(),
                'status': trek.status
            }
        }), 201

    except Exception:
        db.session.rollback()

        return jsonify({
            'message': 'Failed to create trek'
        }), 500


 
@trek_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_treks():

    claims = get_jwt()

    if claims.get('role') not in ['admin', 'staff', 'trekker']:
        return jsonify({
            'message': 'Access denied'
        }), 403

    search = request.args.get('search', '').strip()

    difficulty = request.args.get('difficulty', '').strip()

    status = request.args.get('status', '').strip()

    if difficulty:
        difficulty = difficulty.capitalize()

        if difficulty not in ['Easy', 'Moderate', 'Hard']:
            return jsonify({
                'message': 'Invalid difficulty filter'
            }), 400

    if status:
        if status not in ['Open', 'Full', 'Closed']:
            return jsonify({
                'message': 'Invalid trek status filter'
            }), 400

    # Create unique cache key for each filter combination
    cache_key = (
        f"treks:search={search}:"
        f"difficulty={difficulty}:"
        f"status={status}"
    )

    cached_data = get_cache(cache_key)

    if cached_data is not None:
        print("REDIS CACHE HIT: Treks fetched from Redis")
        return jsonify(cached_data), 200
    print("REDIS CACHE MISS: Fetching treks from database")

    query = db.select(Trek)

    if search:
        query = query.filter(
            db.or_(
                Trek.name.ilike('%' + search + '%'),
                Trek.location.ilike('%' + search + '%')
            )
        )

    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    if status:
        query = query.filter_by(status=status)

    treks = db.session.execute(
        query.order_by(Trek.start_date.asc())
    ).scalars().all()

    trek_list = []

    for trek in treks:
        trek_list.append({
            'id': trek.id,
            'name': trek.name,
            'location': trek.location,
            'description': trek.description,
            'difficulty': trek.difficulty,
            'duration': trek.duration,
            'available_slots': trek.available_slots,
            'start_date': trek.start_date.isoformat(),
            'end_date': trek.end_date.isoformat(),
            'status': trek.status
        })

    response_data = {
        'message': 'Treks fetched successfully',
        'total_treks': len(trek_list),
        'treks': trek_list
    }

    # Store result in Redis for 5 minutes
    set_cache(cache_key, response_data, expiry=300)

    return jsonify(response_data), 200
 
@trek_bp.route('/<int:trek_id>', methods=['PUT'])
@jwt_required()
def update_trek(trek_id):

    claims = get_jwt()

    if claims.get('role') != 'admin':
        return jsonify({
            'message': 'Access denied. Admin privileges required.'
        }), 403

    trek = db.session.get(Trek, trek_id)

    if not trek:
        return jsonify({
            'message': 'Trek not found'
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            'message': 'Request body must contain JSON data'
        }), 400

    try:
        name = data.get('name', trek.name).strip()
        location = data.get('location', trek.location).strip()
        description = data.get('description', trek.description or '').strip()
        difficulty = data.get('difficulty', trek.difficulty).strip().capitalize()

        duration = int(data.get('duration', trek.duration))
        available_slots = int(
            data.get('available_slots', trek.available_slots)
        )

        start_date = datetime.strptime(
            data.get('start_date', trek.start_date.isoformat()),
            '%Y-%m-%d'
        ).date()

        end_date = datetime.strptime(
            data.get('end_date', trek.end_date.isoformat()),
            '%Y-%m-%d'
        ).date()

    except (ValueError, TypeError, AttributeError):
        return jsonify({
            'message': 'Invalid input values or date format'
        }), 400

    if not name or not location:
        return jsonify({
            'message': 'Name and location cannot be empty'
        }), 400

    if difficulty not in ['Easy', 'Moderate', 'Hard']:
        return jsonify({
            'message': 'Invalid difficulty'
        }), 400

    if duration <= 0 or available_slots < 0:
        return jsonify({
            'message': 'Invalid duration or available slots'
        }), 400

    if end_date < start_date:
        return jsonify({
            'message': 'End date cannot be before start date'
        }), 400

    trek.name = name
    trek.location = location
    trek.description = description
    trek.difficulty = difficulty
    trek.duration = duration
    trek.available_slots = available_slots
    trek.start_date = start_date
    trek.end_date = end_date

    if trek.status != 'Closed':
        trek.status = 'Full' if available_slots == 0 else 'Open'

    try:
        db.session.commit()

        clear_cache()

        return jsonify({
            'message': 'Trek updated successfully',
            'trek_id': trek.id,
            'name': trek.name,
            'location': trek.location,
            'difficulty': trek.difficulty,
            'duration': trek.duration,
            'available_slots': trek.available_slots,
            'start_date': trek.start_date.isoformat(),
            'end_date': trek.end_date.isoformat(),
            'status': trek.status
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
            'message': 'Failed to update trek'
        }), 500


@trek_bp.route('/<int:trek_id>', methods=['DELETE'])
@jwt_required()
def delete_trek(trek_id):

    claims = get_jwt()

    if claims.get('role') != 'admin':
        return jsonify({
            'message': 'Access denied. Admin privileges required.'
        }), 403

    trek = db.session.get(Trek, trek_id)

    if not trek:
        return jsonify({
            'message': 'Trek not found'
        }), 404

    # Check whether this trek has bookings
    booking_count = db.session.query(Booking).filter_by(
        trek_id=trek_id
    ).count()

    if booking_count > 0:
        return jsonify({
            'message': 'This trek has booking records and cannot be deleted. You can close the trek instead.'
        }), 409

    try:
        # Remove staff assignments first
        for assignment in trek.staff_assignments:
            db.session.delete(assignment)

        db.session.delete(trek)
        db.session.commit()

        clear_cache()

        return jsonify({
            'message': 'Trek deleted successfully',
            'trek_id': trek_id
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
            'message': 'Failed to delete trek'
        }), 500

 
@trek_bp.route('/<int:trek_id>/staff', methods=['POST'])
@jwt_required()
def assign_staff(trek_id):

    claims = get_jwt()

    if claims.get('role') != 'admin':
        return jsonify({
            'message': 'Access denied. Admin privileges required.'
        }), 403

    data = request.get_json()

    if not data or 'staff_id' not in data:
        return jsonify({
            'message': 'Staff ID is required'
        }), 400

    try:
        staff_id = int(data['staff_id'])
    except (ValueError, TypeError):
        return jsonify({
            'message': 'Invalid staff ID'
        }), 400

    trek = db.session.get(Trek, trek_id)

    if not trek:
        return jsonify({
            'message': 'Trek not found'
        }), 404

    staff = db.session.get(User, staff_id)

    if not staff or staff.role != 'staff':
        return jsonify({
            'message': 'Staff member not found'
        }), 404

    if not staff.is_approved or staff.is_blacklisted:
        return jsonify({
            'message': 'Staff member is not eligible for assignment'
        }), 403

    existing_assignment = db.session.execute(
        db.select(TrekStaff).filter_by(
            trek_id=trek_id,
            staff_id=staff_id
        )
    ).scalar_one_or_none()

    if existing_assignment:
        return jsonify({
            'message': 'Staff member is already assigned to this trek'
        }), 409

    assignment = TrekStaff(
        trek_id=trek_id,
        staff_id=staff_id
    )

    try:
        db.session.add(assignment)
        db.session.commit()

        return jsonify({
            'message': 'Staff assigned successfully',
            'assignment': {
                'trek_id': trek_id,
                'staff_id': staff.id,
                'staff_name': staff.name
            }
        }), 201

    except Exception:
        db.session.rollback()

        return jsonify({
            'message': 'Failed to assign staff'
        }), 500

 
@trek_bp.route('/<int:trek_id>/staff', methods=['GET'])
@jwt_required()
def get_assigned_staff(trek_id):

    claims = get_jwt()

    if claims.get('role') != 'admin':
        return jsonify({
            'message': 'Access denied. Admin privileges required.'
        }), 403

    trek = db.session.get(Trek, trek_id)

    if not trek:
        return jsonify({
            'message': 'Trek not found'
        }), 404

    assignments = db.session.execute(
        db.select(TrekStaff).filter_by(trek_id=trek_id)
    ).scalars().all()

    staff_list = []

    for assignment in assignments:
        staff = assignment.staff

        staff_list.append({
            'staff_id': staff.id,
            'name': staff.name,
            'email': staff.email,
            'phone': staff.phone,
            'assigned_at': assignment.assigned_at.isoformat()
        })

    return jsonify({
        'message': 'Assigned staff fetched successfully',
        'trek_id': trek.id,
        'trek_name': trek.name,
        'total_staff': len(staff_list),
        'staff': staff_list
    }), 200

 
@trek_bp.route('/<int:trek_id>/staff/<int:staff_id>', methods=['DELETE'])
@jwt_required()
def remove_staff(trek_id, staff_id):

    claims = get_jwt()

    if claims.get('role') != 'admin':
        return jsonify({
            'message': 'Access denied. Admin privileges required.'
        }), 403

    trek = db.session.get(Trek, trek_id)

    if not trek:
        return jsonify({
            'message': 'Trek not found'
        }), 404

    assignment = db.session.execute(
        db.select(TrekStaff).filter_by(
            trek_id=trek_id,
            staff_id=staff_id
        )
    ).scalar_one_or_none()

    if not assignment:
        return jsonify({
            'message': 'Staff assignment not found'
        }), 404

    try:
        db.session.delete(assignment)
        db.session.commit()

        return jsonify({
            'message': 'Staff removed from trek successfully',
            'trek_id': trek_id,
            'staff_id': staff_id
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
            'message': 'Failed to remove staff assignment'
        }), 500
