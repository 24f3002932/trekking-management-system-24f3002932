from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from database import db
from models import User
from services.cache import clear_cache

users_bp = Blueprint('users', __name__, url_prefix='/api/users')


@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_users():

    claims = get_jwt()

    if claims.get('role') != 'admin':
        return jsonify({
            'message': 'Access denied. Admin privileges required.'
        }), 403

    search = request.args.get('search', '').strip()

    query = db.select(User).filter_by(role='trekker')

    if search:
        query = query.filter(
            db.or_(
                User.name.ilike('%' + search + '%'),
                User.email.ilike('%' + search + '%')
            )
        )

    users = db.session.execute(
        query.order_by(User.id.desc())
    ).scalars().all()

    user_list = []

    for user in users:
        user_list.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'is_blacklisted': user.is_blacklisted,
            'created_at': user.created_at.isoformat()
        })

    return jsonify({
        'message': 'Users fetched successfully',
        'total_users': len(user_list),
        'users': user_list
    }), 200

 
@users_bp.route('/<int:user_id>/status', methods=['PUT'])
@jwt_required()
def update_user_status(user_id):

    claims = get_jwt()

    if claims.get('role') != 'admin':
        return jsonify({
            'message': 'Access denied. Admin privileges required.'
        }), 403

    user = db.session.get(User, user_id)

    if not user or user.role != 'trekker':
        return jsonify({
            'message': 'Trekker not found'
        }), 404

    data = request.get_json()

    if not data or 'is_blacklisted' not in data:
        return jsonify({
            'message': 'Blacklist status is required'
        }), 400

    if not isinstance(data['is_blacklisted'], bool):
        return jsonify({
            'message': 'is_blacklisted must be true or false'
        }), 400

    try:
        user.is_blacklisted = data['is_blacklisted']

        db.session.commit()
        clear_cache("admin:dashboard")

        return jsonify({
            'message': 'User status updated successfully',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'is_blacklisted': user.is_blacklisted
            }
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
            'message': 'Failed to update user status'
        }), 500
