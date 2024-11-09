from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)  # Should be hashed in practice
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    location = db.Column(db.String(100))

    # Relationship with the Symptoms table
    symptoms = db.relationship('Symptom', backref='user', lazy=True)

class Symptom(db.Model):
    __tablename__ = 'symptoms'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    label = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint to avoid duplicate symptoms for a user
    __table_args__ = (db.UniqueConstraint('userid', 'description', name='unique_user_symptom'),)

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Relaterer til bruker
    action = db.Column(db.String(255), nullable=False)  # Hva brukeren gjorde
    endpoint = db.Column(db.String(100), nullable=False)  # API-endepunkt
    method = db.Column(db.String(10), nullable=False)  # HTTP-metode (GET, POST, osv.)
    ip_address = db.Column(db.String(45))  # IP-adresse til brukeren
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Når handlingen skjedde
    status_code = db.Column(db.Integer)  # HTTP-statuskoden for svaret



    def __repr__(self):
        return f"<ActivityLog user_id={self.user_id} action='{self.action}' endpoint='{self.endpoint}'>"