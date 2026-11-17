from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import User, Notification
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from services.cache import clear_cache


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({
            'message': 'Request body must contain JSON data'
        }), 400

    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    phone = data.get('phone', '').strip()

    if not name or not email or not password:
        return jsonify({
            'message': 'Name, email and password are required'
        }), 400

    if len(password) < 8:
        return jsonify({
            'message': 'Password must contain at least 8 characters'
        }), 400

    existing_user = db.session.execute(
        db.select(User).filter_by(email=email)
    ).scalar_one_or_none()

    if existing_user:
        return jsonify({
            'message': 'An account with this email already exists'
        }), 409

    user = User(
        name=name,
        email=email,
        passhash=generate_password_hash(password),
        role='trekker',
        phone=phone or None,
        is_approved=True
    )

    try:
        db.session.add(user)
        db.session.commit()

        clear_cache("admin:dashboard")

        return jsonify({
            'message': 'Registration successful',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role
            }
        }), 201

    except Exception:
        db.session.rollback()
        return jsonify({
            'message': 'Registration failed due to a server error'
        }), 500

 
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({
            'message': 'Request body must contain JSON data'
        }), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({
            'message': 'Email and password are required'
        }), 400

    user = db.session.execute(
        db.select(User).filter_by(email=email)
    ).scalar_one_or_none()

    if not user or not check_password_hash(user.passhash, password):
        return jsonify({
            'message': 'Invalid email or password'
        }), 401

    if user.is_blacklisted:
        return jsonify({
            'message': 'Your account has been blocked'
        }), 403

    if user.role == 'staff' and not user.is_approved:
        return jsonify({
            'message': 'Your staff account is awaiting approval'
        }), 403

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            'role': user.role
        }
    )

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role
        }
    }), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()

    user = db.session.get(User, int(user_id))

    if not user:
        return jsonify({
            'message': 'User not found'
        }), 404

    return jsonify({
        'message': 'Profile fetched successfully',
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'role': user.role
        }
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():

    # Allow only trekkers
    claims = get_jwt()

    if claims.get('role') != 'trekker':
        return jsonify({
            'message': 'Only trekkers can update this profile.'
        }), 403

    user_id = int(get_jwt_identity())

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({
            'message': 'User not found.'
        }), 404

    if user.is_blacklisted:
        return jsonify({
            'message': 'Your account is blacklisted.'
        }), 403

    data = request.get_json() or {}

    name = data.get('name', user.name)
    email = data.get('email', user.email)
    phone = data.get('phone', user.phone)

    if not name or not email:
        return jsonify({
            'message': 'Name and email cannot be empty.'
        }), 400

    name = name.strip()
    email = email.strip().lower()

    if not name or not email:
        return jsonify({
            'message': 'Name and email cannot be empty.'
        }), 400

    # Check whether email is already registered
    existing_user = db.session.execute(
        db.select(User).filter(
            User.email == email,
            User.id != user_id
        )
    ).scalar_one_or_none()

    if existing_user:
        return jsonify({
            'message': 'Email is already registered.'
        }), 409

    user.name = name
    user.email = email
    user.phone = phone.strip() if phone else None

    db.session.commit()

    return jsonify({
        'message': 'Profile updated successfully.',
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'role': user.role
        }
    }), 200

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():

    # Allow only trekkers
    claims = get_jwt()

    if claims.get('role') != 'trekker':
        return jsonify({
            'message': 'Only trekkers can change their password.'
        }), 403

    user_id = int(get_jwt_identity())

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({
            'message': 'User not found.'
        }), 404

    if user.is_blacklisted:
        return jsonify({
            'message': 'Your account is blacklisted.'
        }), 403

    data = request.get_json() or {}

    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    # Validate input
    if not old_password or not new_password:
        return jsonify({
            'message': 'Current and new passwords are required.'
        }), 400

    if len(new_password) < 8:
        return jsonify({
            'message': 'New password must contain at least 8 characters.'
        }), 400

    # Verify current password
    if not check_password_hash(user.passhash, old_password):
        return jsonify({
            'message': 'Current password is incorrect.'
        }), 401

    if old_password == new_password:
        return jsonify({
            'message': 'New password must be different from current password.'
        }), 400

    # Hash and update new password
    user.passhash = generate_password_hash(new_password)

    db.session.commit()

    return jsonify({
        'message': 'Password changed successfully.'
    }), 200

@auth_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():

    user_id = int(get_jwt_identity())

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({
            'message': 'User not found.'
        }), 404

    if user.is_blacklisted:
        return jsonify({
            'message': 'Your account is blacklisted.'
        }), 403

    notifications = db.session.execute(
        db.select(Notification)
        .filter_by(user_id=user_id)
        .order_by(Notification.created_at.desc())
    ).scalars().all()

    notification_list = []

    for notification in notifications:
        notification_list.append({
            'notification_id': notification.id,
            'message': notification.message,
            'status': notification.status,
            'created_at': notification.created_at.isoformat()
        })

    return jsonify({
        'message': 'Notifications fetched successfully.',
        'total_notifications': len(notification_list),
        'notifications': notification_list
    }), 200

@auth_bp.route('/notifications/<int:notification_id>/read',methods=['PUT'])
@jwt_required()
def mark_notification_read(notification_id):

    user_id = int(get_jwt_identity())

    notification = db.session.execute(
        db.select(Notification).filter_by(
            id=notification_id,
            user_id=user_id
        )
    ).scalar_one_or_none()

    if not notification:
        return jsonify({
            'message': 'Notification not found.'
        }), 404

    notification.status = 'Read'

    db.session.commit()

    return jsonify({
        'message': 'Notification marked as read.',
        'notification_id': notification.id,
        'status': notification.status
    }), 200
