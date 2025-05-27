from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import foreign, remote

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone_number = db.Column(db.String(20))
    
    # Relationship to bookings
    bookings = db.relationship('Booking', backref='customer', lazy=True)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone_number = db.Column(db.String(20))

class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone_number = db.Column(db.String(20))
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    price = db.Column(db.Float)
    media = db.Column(db.String(200))
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    
    # Relationship to bookings
    bookings = db.relationship('Booking',
                             primaryjoin="and_(foreign(Venue.id)==remote(Booking.service_id), "
                                       "Booking.service_type=='venue')",
                             backref=db.backref('venue_service', uselist=False),
                             lazy=True)

class Hairdresser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone_number = db.Column(db.String(20))
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    price = db.Column(db.Float)
    media = db.Column(db.String(200))
    approval_status = db.Column(db.String(20), default='pending')
    
    # Relationship to bookings
    bookings = db.relationship('Booking',
                             primaryjoin="and_(foreign(Hairdresser.id)==remote(Booking.service_id), "
                                       "Booking.service_type=='hairdresser')",
                             backref=db.backref('hairdresser_service', uselist=False),
                             lazy=True)

class Weddingplanner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone_number = db.Column(db.String(20))
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    price = db.Column(db.Float)
    media = db.Column(db.String(200))
    approval_status = db.Column(db.String(20), default='pending')
    
    # Relationship to bookings
    bookings = db.relationship('Booking',
                             primaryjoin="and_(foreign(Weddingplanner.id)==remote(Booking.service_id), "
                                       "Booking.service_type=='weddingplanner')",
                             backref=db.backref('weddingplanner_service', uselist=False),
                             lazy=True)

class Makeupartist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone_number = db.Column(db.String(20))
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    price = db.Column(db.Float)
    media = db.Column(db.String(200))
    approval_status = db.Column(db.String(20), default='pending')
    
    # Relationship to bookings
    bookings = db.relationship('Booking',
                             primaryjoin="and_(foreign(Makeupartist.id)==remote(Booking.service_id), "
                                       "Booking.service_type=='makeupartist')",
                             backref=db.backref('makeupartist_service', uselist=False),
                             lazy=True)

class Venuedetails(db.Model):
    name = db.Column(db.String(180), primary_key=True, unique=True, nullable=False)
    email = db.Column(db.String(120))
    phone_number = db.Column(db.String(20))
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    price = db.Column(db.Float)
    media = db.Column(db.String(200))

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key to User (customer who is booking)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Service type and ID
    service_type = db.Column(db.String(20), nullable=False)  # 'venue', 'makeupartist', 'hairdresser', 'weddingplanner'
    service_id = db.Column(db.Integer, nullable=False)
    
    # Booking details
    booking_date = db.Column(db.Date, nullable=False)  # Date of the actual service
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # When booking was made
    
    # Booking status
    status = db.Column(db.String(20), default='pending')  # 'pending', 'confirmed', 'cancelled', 'completed'
    
    def __repr__(self):
        return f'<Booking {self.id}: User {self.user_id} -> {self.service_type} {self.service_id} on {self.booking_date}>'
    
    @property
    def service(self):
        """Get the service object based on service_type and service_id"""
        if self.service_type == 'venue':
            return self.venue_service
        elif self.service_type == 'makeupartist':
            return self.makeupartist_service
        elif self.service_type == 'hairdresser':
            return self.hairdresser_service
        elif self.service_type == 'weddingplanner':
            return self.weddingplanner_service
        return None