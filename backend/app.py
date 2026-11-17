from flask import Flask, jsonify
from config import SECRET_KEY, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from flask_jwt_extended import JWTManager
from database import db
from models import User
from werkzeug.security import generate_password_hash

from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.treks import trek_bp
from routes.staff import staff_bp
from routes.users import users_bp
from routes.bookings import bookings_bp

app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

db.init_app(app)
jwt = JWTManager(app)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(trek_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(users_bp)
app.register_blueprint(bookings_bp)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Trekking Management System API is running!",
        "status": "success"
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "message": "Backend is healthy",
        "status": "success"
    })


@app.route("/api/db-health", methods=["GET"])
def database_health():
    try:
        db.session.execute(db.text("SELECT 1"))
        return jsonify({
            "message": "Database connection successful",
            "status": "success"
        })
    except Exception:
        db.session.rollback()
        return jsonify({
            "message": "Database connection failed",
            "status": "error"
        }), 500

if __name__ == "__main__":

    with app.app_context():

        db.create_all()

        # Default Admin Credentials
        ADMIN_NAME = "System Admin"
        ADMIN_EMAIL = "admin@trek.com"
        ADMIN_PASSWORD = "admin123"

        existing_admin = db.session.execute(
            db.select(User).filter_by(email=ADMIN_EMAIL)
        ).scalar_one_or_none()

        if not existing_admin:

            admin = User(
                name=ADMIN_NAME,
                email=ADMIN_EMAIL,
                passhash=generate_password_hash(ADMIN_PASSWORD),
                role="admin",
                is_approved=True,
                is_blacklisted=False
            )

            db.session.add(admin)
            db.session.commit()

            print("Default Admin Created Successfully!")

        else:
            print("Admin Account Already Exists!")

    app.run(debug=True)
