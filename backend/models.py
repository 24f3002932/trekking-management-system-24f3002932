from database import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    passhash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(15))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    staff_profile = db.relationship(
        'StaffProfile', backref='user', uselist=False
    )

    bookings = db.relationship('Booking', backref='user', lazy=True)

    notifications = db.relationship(
        'Notification', backref='user', lazy=True
    )

    job_exports = db.relationship(
        'JobExport', backref='user', lazy=True
    )


class StaffProfile(db.Model):
    __tablename__ = 'staff_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'),
        unique=True, nullable=False
    )
    experience = db.Column(db.Integer, default=0)
    specialization = db.Column(db.String(100))
    contact = db.Column(db.String(15))


class Trek(db.Model):
    __tablename__ = 'treks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    difficulty = db.Column(db.String(20), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False, default=0)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', backref='trek', lazy=True)

    staff_assignments = db.relationship(
        'TrekStaff', backref='trek', lazy=True
    )


class TrekStaff(db.Model):
    __tablename__ = 'trek_staff'

    id = db.Column(db.Integer, primary_key=True)
    trek_id = db.Column(
        db.Integer, db.ForeignKey('treks.id'), nullable=False
    )
    staff_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False
    )
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    staff = db.relationship('User', backref='trek_assignments')

    __table_args__ = (
        db.UniqueConstraint(
            'trek_id', 'staff_id',
            name='unique_trek_staff'
        ),
    )


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False
    )
    trek_id = db.Column(
        db.Integer, db.ForeignKey('treks.id'), nullable=False
    )
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Booked')

    


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False
    )
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Unread')


class JobExport(db.Model):
    __tablename__ = 'job_exports'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False
    )
    status = db.Column(db.String(20), nullable=False, default='Pending')
    file_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)