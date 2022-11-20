"""Utilized to store tables within the sql database"""
from website import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    """This class is the user model that will hold all user data moving 
    forward. For example, prescriptions, medical history, authentication 
    codes, etc."""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    user_name = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    weight = db.Column(db.Integer)
    height = db.Column(db.Integer)
    ethnicity = db.Column(db.String(150))
    birthday = db.Column(db.String(150))
    age = db.Column(db.Integer)
    blood = db.Column(db.String(150))
    appointments = db.relationship('Appointments')
    is_doctor = db.Column(db.Boolean, default=False, nullable=False)


class FailedAttempts(db.Model):
    """This class is utilized to store security data. The intent is to
    have a log of every failed login attempt to prevent bruteforce attacks
    and limit vulnerabilities."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150))
    ip = db.Column(db.Integer)
    date = db.Column(db.Integer)
    location = db.Column(db.String(300))


class Appointments(db.Model):
    """This class is utilized to store user appointment data. A foreign
    key is utilized to form a relationship between appointments and the User
    model."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    doctor = db.Column(db.String(150))
    date = db.Column(db.Integer)
    time = db.Column(db.Integer)
    patient_concerns = db.Column(db.String(10000))
    doctor_notes = db.Column(db.String(10000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.patient_id'))

