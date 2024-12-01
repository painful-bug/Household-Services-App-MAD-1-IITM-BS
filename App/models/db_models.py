from App import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from enum import Enum

# Enum


# class UserRole(Enum):
#     ADMIN = 'admin'
#     PROFESSIONAL = 'professional'
#     CUSTOMER = 'customer'


class User(db.Model, UserMixin):
    # UPDATED SCHEMA
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    middle_name = db.Column(db.String(150), nullable=True)
    last_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=True, default="customer")
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_blocked = db.Column(db.Boolean, default=False)
    block_reason = db.Column(db.String(50), nullable=True)

    professional_profile = db.relationship(
        'Professional', backref='user', uselist=False)
    customer_profile = db.relationship(
        'Customer', backref='user', uselist=False)

    @property
    def password(self):
        # raise AttributeError("Password not secure")
        pass

    @password.setter
    def password(self, password_):
        self.password_hash = generate_password_hash(password_)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'email': self.email,
            'role': self.role
        }


class Professional(db.Model):
    __tablename__ = 'professionals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # full_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    experience_years = db.Column(db.Integer)
    service_id = db.Column(db.Integer, db.ForeignKey(
        'services.id'), nullable=True)
    preferred_service = db.Column(db.String(100), default="general")
    is_verified = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, default=0.0)
    location_pincode = db.Column(db.String(10))
    document_verification_status = db.Column(db.String(20), default='pending')
    is_available = db.Column(db.Boolean, default=True)
    rejection_reason = db.Column(db.Text)

    service_requests = db.relationship(
        'ServiceRequest', backref='professional')
    reviews = db.relationship('Review', backref='professional')
   

class Docs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False)
    filename = db.Column(db.String(50))
    data = db.Column(db.LargeBinary)
    

    professional = db.relationship('Professional', backref='documents')

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    phone = db.Column(db.String(15))
    address = db.Column(db.Text)
    location_pincode = db.Column(db.String(10))

    service_requests = db.relationship('ServiceRequest', backref='customer')
    reviews = db.relationship('Review', backref='customer')


class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    base_price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.String(50)) 
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now)


    professionals = db.relationship('Professional', backref='service')
    service_requests = db.relationship('ServiceRequest', backref='service')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'base_price': self.base_price,
            'time_required': self.time_required,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey(
        'services.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey(
        'customers.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'))

    date_of_request = db.Column(db.DateTime, default=datetime.now)
    preferred_date = db.Column(db.DateTime, nullable=False)
    date_of_completion = db.Column(db.DateTime)
    # requested, assigned, rejected, completed, closed
    status = db.Column(db.String(20), default='requested')
    remarks = db.Column(db.Text)
    #! OPTIONAL attributes might delete
    # location_pincode = db.Column(db.String(10))
    # total_amount = db.Column(db.Float)

    # Relationship with Review
    review = db.relationship(
        'Review', backref='service_request', uselist=False)


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey(
        'service_requests.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey(
        'customers.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey(
        'professionals.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
