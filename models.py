from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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
    
    # Relationship to bookings
    bookings = db.relationship('Booking', backref='venue_service', lazy=True)

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
    
    # Foreign key to Venue (venue being booked)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    
    # Booking details
    booking_date = db.Column(db.Date, nullable=False)  # Date of the actual service
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # When booking was made
    
    # Booking status
    status = db.Column(db.String(20), default='pending')  # 'pending', 'confirmed', 'cancelled', 'completed'
    
    def __repr__(self):
        return f'<Booking {self.id}: User {self.user_id} -> Venue {self.venue_id} on {self.booking_date}>'