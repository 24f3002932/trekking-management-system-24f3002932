from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from werkzeug.security import generate_password_hash

from database import db
from models import User, StaffProfile, TrekStaff, Booking, Trek
from services.cache import clear_cache

staff_bp = Blueprint('staff', __name__, url_prefix='/api/staff')


@staff_bp.route('/', methods=['POST'])
@jwt_required()
def create_staff():

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

    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    phone = data.get('phone', '').strip()
    specialization = data.get('specialization', '').strip()
    contact = data.get('contact', '').strip()

    try:
        experience = int(data.get('experience', 0))
    except (ValueError, TypeError):
        return jsonify({
            'message': 'Experience must be a valid number'
        }), 400

    if not name or not email or not password:
        return jsonify({
            'message': 'Name, email and password are required'
        }), 400

    if len(password) < 8:
        return jsonify({
            'message': 'Password must contain at least 8 characters'
        }), 400

    if experience < 0:
        return jsonify({
            'message': 'Experience cannot be negative'
        }), 400

    existing_user = db.session.execute(
        db.select(User).filter_by(email=email)
    ).scalar_one_or_none()

    if existing_user:
        return jsonify({
            'message': 'An account with this email already exists'
        }), 409

    staff = User(
        name=name,
        email=email,
        passhash=generate_password_hash(password),
        role='staff',
        phone=phone or None,
        is_approved=True,
        is_blacklisted=False
    )

    try:
        db.session.add(staff)
        db.session.flush()

        staff_profile = StaffProfile(
            user_id=staff.id,
            experience=experience,
            specialization=specialization or None,
            contact=contact or None
        )

        db.session.add(staff_profile)
        db.session.commit()

        clear_cache("admin:dashboard")

        return jsonify({
            'message': 'Staff account created successfully',
            'staff': {
                'id': staff.id,
                'name': staff.name,
                'email': staff.email,
                'role': staff.role,
                'experience': staff_profile.experience,
                'specialization': staff_profile.specialization
            }
        }), 201

    except Exception:
        db.session.rollback()

        return jsonify({
            'message': 'Failed to create staff account'
        }), 500

 
@staff_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_staff():

    claims = get_jwt()

    if claims.get('role') != 'admin':
        return jsonify({
            'message': 'Access denied. Admin privileges required.'
        }), 403

    search = request.args.get('search', '').strip()

    query = db.select(User).filter_by(role='staff')

    if search:
        query = query.filter(
            db.or_(
                User.name.ilike('%' + search + '%'),
                User.email.ilike('%' + search + '%')
            )
        )

    staff_members = db.session.execute(
        query.order_by(User.id.desc())
    ).scalars().all()

    staff_list = []

    for staff in staff_members:

        profile = staff.staff_profile

        staff_list.append({
            'id': staff.id,
            'name': staff.name,
            'email': staff.email,
            'phone': staff.phone,
            'is_approved': staff.is_approved,
            'is_blacklisted': staff.is_blacklisted,
            'experience': profile.experience if profile else 0,
            'specialization': profile.specialization if profile else None,
            'contact': profile.contact if profile else None
        })

    return jsonify({
        'message': 'Staff members fetched successfully',
        'total_staff': len(staff_list),
        'staff': staff_list
    }), 200

 
@staff_bp.route('/<int:staff_id>', methods=['PUT'])
@jwt_required()
def update_staff(staff_id):

    claims = get_jwt()

    if claims.get('role') != 'admin':
        return jsonify({
            'message': 'Access denied. Admin privileges required.'
        }), 403

    staff = db.session.get(User, staff_id)

    if not staff or staff.role != 'staff':
        return jsonify({
            'message': 'Staff member not found'
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            'message': 'Request body must contain JSON data'
        }), 400

    name = data.get('name', staff.name)
    email = data.get('email', staff.email)

    if not isinstance(name, str) or not isinstance(email, str):
        return jsonify({
            'message': 'Name and email must be valid text'
        }), 400

    name = name.strip()
    email = email.strip().lower()

    if not name or not email:
        return jsonify({
            'message': 'Name and email cannot be empty'
        }), 400

    existing_user = db.session.execute(
        db.select(User).filter(
            User.email == email,
            User.id != staff_id
        )
    ).scalar_one_or_none()

    if existing_user:
        return jsonify({
            'message': 'Email is already registered'
        }), 409

    phone = data.get('phone', staff.phone)

    if phone is not None and not isinstance(phone, str):
        return jsonify({
            'message': 'Phone must be valid text'
        }), 400

    password = data.get('password')

    if password is not None:
        if not isinstance(password, str) or len(password) < 8:
            return jsonify({
                'message': 'Password must contain at least 8 characters'
            }), 400

        staff.passhash = generate_password_hash(password)

    profile = staff.staff_profile

    if not profile:
        profile = StaffProfile(user_id=staff.id)
        db.session.add(profile)

    try:
        experience = int(
            data.get('experience', profile.experience or 0)
        )

        if experience < 0:
            return jsonify({
                'message': 'Experience cannot be negative'
            }), 400

        specialization = data.get(
            'specialization', profile.specialization
        )

        contact = data.get('contact', profile.contact)

        if specialization is not None and not isinstance(specialization, str):
            return jsonify({
                'message': 'Specialization must be text'
            }), 400

        if contact is not None and not isinstance(contact, str):
            return jsonify({
                'message': 'Contact must be text'
            }), 400

        staff.name = name
        staff.email = email
        staff.phone = phone.strip() if phone else None

        profile.experience = experience
        profile.specialization = (
            specialization.strip() if specialization else None
        )
        profile.contact = contact.strip() if contact else None

        db.session.commit()

        clear_cache("admin:dashboard")

        return jsonify({
            'message': 'Staff details updated successfully',
            'staff': {
                'id': staff.id,
                'name': staff.name,
                'email': staff.email,
                'phone': staff.phone,
                'experience': profile.experience,
                'specialization': profile.specialization,
                'contact': profile.contact
            }
        }), 200

    except (ValueError, TypeError):
        db.session.rollback()
        return jsonify({
            'message': 'Invalid experience value'
        }), 400

    except Exception:
        db.session.rollback()
        return jsonify({
            'message': 'Failed to update staff details'
        }), 500

 
@staff_bp.route('/<int:staff_id>/status', methods=['PUT'])
@jwt_required()
def update_staff_status(staff_id):

    claims = get_jwt()

    if claims.get('role') != 'admin':
        return jsonify({
            'message': 'Access denied. Admin privileges required.'
        }), 403

    staff = db.session.get(User, staff_id)

    if not staff or staff.role != 'staff':
        return jsonify({
            'message': 'Staff member not found'
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            'message': 'Request body must contain JSON data'
        }), 400

    if 'is_approved' not in data and 'is_blacklisted' not in data:
        return jsonify({
            'message': 'Provide approval or blacklist status'
        }), 400

    if 'is_approved' in data:
        if not isinstance(data['is_approved'], bool):
            return jsonify({
                'message': 'is_approved must be true or false'
            }), 400

    if 'is_blacklisted' in data:
        if not isinstance(data['is_blacklisted'], bool):
            return jsonify({
                'message': 'is_blacklisted must be true or false'
            }), 400

    try:
        if data.get('is_blacklisted') is True:
            staff.is_blacklisted = True
            staff.is_approved = False

        elif data.get('is_blacklisted') is False:
            staff.is_blacklisted = False

        if 'is_approved' in data:
            if data['is_approved'] and staff.is_blacklisted:
                return jsonify({
                    'message': 'Unblacklist the staff member before approving'
                }), 400

            staff.is_approved = data['is_approved']

        db.session.commit()

        clear_cache("admin:dashboard")
        
        return jsonify({
            'message': 'Staff status updated successfully',
            'staff': {
                'id': staff.id,
                'name': staff.name,
                'is_approved': staff.is_approved,
                'is_blacklisted': staff.is_blacklisted
            }
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
            'message': 'Failed to update staff status'
        }), 500


@staff_bp.route('/my-treks', methods=['GET'])
@jwt_required()
def get_my_treks():

    claims = get_jwt()

    if claims.get('role') != 'staff':
        return jsonify({
            'message': 'Only staff members can access this resource'
        }), 403

    staff_id = int(get_jwt_identity())

    staff = db.session.get(User, staff_id)

    if not staff or staff.is_blacklisted or not staff.is_approved:
        return jsonify({
            'message': 'Your staff account is not eligible'
        }), 403

    assignments = db.session.execute(
        db.select(TrekStaff).filter_by(staff_id=staff_id)
    ).scalars().all()

    trek_list = []

    for assignment in assignments:

        trek = assignment.trek

        if not trek:
            continue

        trek_list.append({
            'trek_id': trek.id,
            'name': trek.name,
            'location': trek.location,
            'description': trek.description,
            'difficulty': trek.difficulty,
            'duration': trek.duration,
            'available_slots': trek.available_slots,
            'start_date': trek.start_date.isoformat(),
            'end_date': trek.end_date.isoformat(),
            'status': trek.status,
            'assigned_at': assignment.assigned_at.isoformat()
        })

    return jsonify({
        'message': 'Assigned treks fetched successfully',
        'total_treks': len(trek_list),
        'treks': trek_list
    }), 200

@staff_bp.route('/my-treks/<int:trek_id>/participants', methods=['GET'])
@jwt_required()
def get_trek_participants(trek_id):

    # Check staff role
    claims = get_jwt()

    if claims.get('role') != 'staff':
        return jsonify({
            'message': 'Access denied. Staff only.'
        }), 403

    staff_id = int(get_jwt_identity())

    # Check staff account
    staff = db.session.get(User, staff_id)

    if not staff or staff.is_blacklisted or not staff.is_approved:
        return jsonify({
            'message': 'Staff account is not active.'
        }), 403

    # Check whether this trek is assigned to the staff
    assignment = db.session.execute(
        db.select(TrekStaff).filter_by(
            trek_id=trek_id,
            staff_id=staff_id
        )
    ).scalar_one_or_none()

    if not assignment:
        return jsonify({
            'message': 'You are not assigned to this trek.'
        }), 403

    # Fetch active bookings for this trek
    bookings = db.session.execute(
        db.select(Booking)
        .filter_by(
            trek_id=trek_id,
            status='Booked'
        )
        .order_by(Booking.booking_date.asc())
    ).scalars().all()

    participants = []

    for booking in bookings:
        user = booking.user

        if not user:
            continue

        participants.append({
            'booking_id': booking.id,
            'participant_id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'booking_date': booking.booking_date.isoformat(),
            'status': booking.status
        })

    return jsonify({
        'message': 'Participants fetched successfully.',
        'trek_id': trek_id,
        'total_participants': len(participants),
        'participants': participants
    }), 200

@staff_bp.route('/my-treks/<int:trek_id>/manage', methods=['PUT'])
@jwt_required()
def manage_assigned_trek(trek_id):

    # Check staff role
    claims = get_jwt()

    if claims.get('role') != 'staff':
        return jsonify({
            'message': 'Access denied. Staff only.'
        }), 403

    staff_id = int(get_jwt_identity())

    # Check staff account
    staff = db.session.get(User, staff_id)

    if not staff or staff.is_blacklisted or not staff.is_approved:
        return jsonify({
            'message': 'Staff account is not active.'
        }), 403

    # Check trek assignment
    assignment = db.session.execute(
        db.select(TrekStaff).filter_by(
            trek_id=trek_id,
            staff_id=staff_id
        )
    ).scalar_one_or_none()

    if not assignment:
        return jsonify({
            'message': 'You are not assigned to this trek.'
        }), 403

    trek = db.session.get(Trek, trek_id)

    if not trek:
        return jsonify({
            'message': 'Trek not found.'
        }), 404

    data = request.get_json() or {}

    if 'available_slots' not in data or 'status' not in data:
        return jsonify({
            'message': 'Available slots and status are required.'
        }), 400

    try:
        slots = int(data['available_slots'])
    except (ValueError, TypeError):
        return jsonify({
            'message': 'Available slots must be a valid integer.'
        }), 400

    status = data['status']

    if slots < 0:
        return jsonify({
            'message': 'Available slots cannot be negative.'
        }), 400

    if status not in ['Open', 'Closed']:
        return jsonify({
            'message': 'Status must be Open or Closed.'
        }), 400

    # Count active bookings
    booked = db.session.execute(
        db.select(db.func.count(Booking.id)).filter_by(
            trek_id=trek_id,
            status='Booked'
        )
    ).scalar_one()

    if slots < booked:
        return jsonify({
            'message': f'Available slots cannot be less than booked participants ({booked}).'
        }), 400

    # Update trek
    trek.available_slots = slots

    if status == 'Closed':
        trek.status = 'Closed'
    elif slots == 0:
        trek.status = 'Full'
    else:
        trek.status = 'Open'

    db.session.commit()

    return jsonify({
        'message': 'Trek updated successfully.',
        'trek': {
            'trek_id': trek.id,
            'name': trek.name,
            'available_slots': trek.available_slots,
            'status': trek.status,
            'booked_participants': booked
        }
    }), 200
