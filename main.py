from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Venue, Admin, Makeupartist, Weddingplanner, Hairdresser, Venuedetails, Booking
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.secret_key = "your_secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# Service configuration
SERVICE_CONFIG = {
    'venue': {
        'model': Venue,
        'title': 'Wedding Venues',
        'detail_route': 'venuedetails'
    },
    'hairdresser': {
        'model': Hairdresser,
        'title': 'Hair Dressers',
        'detail_route': 'hairdresserdetails'
    },
    'weddingplanner': {
        'model': Weddingplanner,
        'title': 'Wedding Planners',
        'detail_route': 'weddingplannerdetails'
    },
    'makeupartist': {
        'model': Makeupartist,
        'title': 'Makeup Artists',
        'detail_route': 'makeupartistdetails'
    }
}

# HTML routes
@app.route("/")
def home():
    return render_template("home_page.html") 

@app.route("/booking")
@app.route("/booking/<int:venue_id>")
def booking(venue_id=None):
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if venue_id:
        venue = Venue.query.get(venue_id)
        if not venue:
            return "Venue not found", 404
        return render_template("booking.html", venue=venue, datetime=datetime, timedelta=timedelta)
    else:
        return render_template("booking.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

# Dynamic service routes
@app.route("/services")
@app.route("/services/<service_type>")
def services(service_type='venue'):
    if service_type not in SERVICE_CONFIG:
        return "Service not found", 404
    
    config = SERVICE_CONFIG[service_type]
    services_data = config['model'].query.all()
    
    return render_template("services.html", 
                         services=services_data, 
                         service_type=service_type,
                         title=config['title'])

# Legacy routes for backward compatibility
@app.route("/venue")
def venue():
    return redirect(url_for('services', service_type='venue'))

@app.route("/hairdresser")
def hairdresser():
    return redirect(url_for('services', service_type='hairdresser'))

@app.route("/weddingplanner")
def weddingplanner():
    return redirect(url_for('services', service_type='weddingplanner'))

@app.route("/makeupartist")
def makeupartist():
    return redirect(url_for('services', service_type='makeupartist'))

# API endpoint for dynamic loading
@app.route("/api/services/<service_type>")
def api_services(service_type):
    if service_type not in SERVICE_CONFIG:
        return jsonify({"error": "Service not found"}), 404
    
    config = SERVICE_CONFIG[service_type]
    services_data = config['model'].query.all()
    
    # Convert to JSON format
    services_json = []
    for service in services_data:
        # Handle media path
        image_filename = ""
        if service.media:
            image_filename = service.media.split('\\')[-1].split('/')[-1]
        
        services_json.append({
            'id': service.id,
            'username': service.username,
            'description': service.description or '',
            'location': getattr(service, 'location', ''),
            'price': getattr(service, 'price', 0),
            'image': image_filename,
            'detail_url': f'/{config["detail_route"]}/{service.username}'
        })
    
    return jsonify({
        'services': services_json,
        'title': config['title'],
        'service_type': service_type
    })

# Detail routes
@app.route('/service_details/<service_type>/<string:name>')
def service_details(service_type, name):
    if service_type not in SERVICE_CONFIG:
        return "Service type not found", 404
    
    config = SERVICE_CONFIG[service_type]
    service = config['model'].query.filter_by(username=name).first()
    
    if service:
        return render_template('service_details.html', 
                             service=service,
                             service_type=service_type)
    else:
        return f"{service_type.title()} not found", 404

# Legacy routes for backward compatibility
@app.route('/venuedetails/<string:name>')
def venue_details(name):
    return redirect(url_for('service_details', service_type='venue', name=name))

@app.route('/hairdresserdetails/<string:name>')
def hairdresser_details(name):
    return redirect(url_for('service_details', service_type='hairdresser', name=name))

@app.route('/makeupartistdetails/<string:name>')
def makeupartist_details(name):
    return redirect(url_for('service_details', service_type='makeupartist', name=name))
    
@app.route('/weddingplannerdetails/<string:name>')
def weddingplanner_details(name):
    return redirect(url_for('service_details', service_type='weddingplanner', name=name))

# Controller routes 
@app.before_request
def log_request_info():
    print("----- New Request -----")
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    print(f"Headers: {dict(request.headers)}")
    print(f"Body: {request.get_data(as_text=True)}")
    print("------------------------")

@app.route('/login_user', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    role_model = {
        "user": User,
        "venue": Venue,
        "hair_dresser": Hairdresser,
        "makeup_artist": Makeupartist,
        "wedding_planner": Weddingplanner,
        "admin": Admin
    }.get(role)

    if not role_model:
        return jsonify({"result": "Invalid role"}), 400

    user = role_model.query.filter_by(username=username, password=password).first()

    if user:
        session['username'] = user.username
        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "Invalid username or password"}), 401

@app.route('/register_user', methods=['POST'])
def register_user():
    select_value = request.form.get('select_value')

    username = request.form.get('username')
    password = request.form.get('password')
    phone_number = request.form.get('phone_number')
    email = request.form.get('email')
    description = request.form.get('description')
    location = request.form.get('location')
    price = request.form.get('price')
    media_file = request.files.get('media')

    media_path = None
    if media_file:
        import os
        from werkzeug.utils import secure_filename
        filename = secure_filename(media_file.filename)
        save_path = os.path.join('static', 'images', filename)
        media_file.save(save_path)
        media_path = f'{filename}'

    # Use the right model based on role
    if select_value == "user":
        new_user = User(
            username=username,
            password=password,
            email=email,
            phone_number=phone_number
        )
    elif select_value == "admin":
        new_user = Admin(
            username=username,
            password=password,
            email=email,
            phone_number=phone_number
        )
    elif select_value == "venue":
        new_user = Venue(
            username=username,
            password=password,
            phone_number=phone_number,
            description=description,
            location=location,
            price=price,
            media=media_path
        )
    elif select_value == "hair_dresser":
        new_user = Hairdresser(
            username=username,
            password=password,
            phone_number=phone_number,
            description=description,
            location=location,
            price=price,
            media=media_path
        )
    elif select_value == "makeup_artist":
        new_user = Makeupartist(
            username=username,
            password=password,
            phone_number=phone_number,
            description=description,
            location=location,
            price=price,
            media=media_path
        )
    elif select_value == "wedding_planner":
        new_user = Weddingplanner(
            username=username,
            password=password,
            phone_number=phone_number,
            description=description,
            price=price,
            media=media_path
        )
    else:
        return jsonify({"success": False, "message": "Invalid role"}), 400

    db.session.add(new_user)
    db.session.commit()

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"success": True, "message": "User registered successfully"})

@app.route('/create_booking', methods=['POST'])
def create_booking():
    """Create a new booking"""
    if 'username' not in session:
        return jsonify({"success": False, "message": "Please log in first"}), 401
    
    try:
        # Get user from session
        user = User.query.filter_by(username=session['username']).first()
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404
        
        # Get form data
        venue_id = int(request.form.get('venue_id'))
        booking_date = request.form.get('date')
        
        # Validate venue exists
        venue = Venue.query.get(venue_id)
        if not venue:
            return jsonify({"success": False, "message": "Venue not found"}), 404
        
        # Convert string date to date object
        booking_date_obj = datetime.strptime(booking_date, '%Y-%m-%d').date()
        
        # Check if venue is already booked on this date
        existing_booking = Booking.query.filter_by(
            venue_id=venue_id,
            booking_date=booking_date_obj
        ).filter(Booking.status != 'cancelled').first()
        
        if existing_booking:
            return jsonify({
                "success": False, 
                "message": "Sorry, this venue is already booked on the selected date"
            }), 400
        
        # Create booking
        booking = Booking(
            user_id=user.id,
            venue_id=venue_id,
            booking_date=booking_date_obj
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": f"Booking created successfully! Your booking ID is {booking.id}",
            "booking_id": booking.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False, 
            "message": f"Error creating booking: {str(e)}"
        }), 500

@app.route('/check_venue_availability', methods=['POST'])
def check_venue_availability():
    """Check if a venue is available on a specific date"""
    try:
        data = request.get_json()
        venue_id = int(data.get('venue_id'))
        booking_date = data.get('date')
        
        # Validate venue exists
        venue = Venue.query.get(venue_id)
        if not venue:
            return jsonify({"available": False, "error": "Venue not found"}), 404
        
        # Convert string date to date object
        booking_date_obj = datetime.strptime(booking_date, '%Y-%m-%d').date()
        
        # Check for existing bookings (excluding cancelled ones)
        existing_booking = Booking.query.filter_by(
            venue_id=venue_id,
            booking_date=booking_date_obj
        ).filter(Booking.status != 'cancelled').first()
        
        return jsonify({"available": existing_booking is None})
        
    except Exception as e:
        return jsonify({"available": False, "error": str(e)}), 500

@app.route('/my_bookings')
def my_bookings():
    """Show user's bookings"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return redirect(url_for('login'))
    
    bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.created_at.desc()).all()
    return render_template('my_bookings.html', bookings=bookings)

if __name__ == '__main__':
    app.run(debug=True, port=5001)