from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response, flash, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from models import db, User, Admin, Venue, Makeupartist, Weddingplanner, Hairdresser, Venuedetails, Booking, ProviderUpdate, Review, ServiceImage
from datetime import datetime, timedelta
from sqlalchemy.orm import foreign, remote, joinedload
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Use environment variables for configuration
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///mydb.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'ali2107767@miuegypt.edu.eg')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'etbc flpx vuem pwks')
app.config['MAIL_DEFAULT_SENDER'] = ('Wedding Services', os.environ.get('MAIL_USERNAME', 'ali2107767@miuegypt.edu.eg'))
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_DEBUG'] = os.environ.get('MAIL_DEBUG', 'True').lower() == 'true'

# Initialize extensions
db.init_app(app)
mail = Mail(app)

# Ensure the upload directory exists
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'images')
EDIT_IMAGES_FOLDER = os.path.join(app.root_path, 'static', 'images', 'edit images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EDIT_IMAGES_FOLDER, exist_ok=True)

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
    try:
        # Get locations and names for each service type
        service_data = {
            'venue': {
                'locations': [str(loc[0]) for loc in db.session.query(Venue.location)
                            .filter(Venue.location.isnot(None))
                            .filter(Venue.approval_status == 'approved')
                            .distinct().all()],
                'providers': [str(name[0]) for name in db.session.query(Venue.username)
                            .filter(Venue.approval_status == 'approved')
                            .distinct().all()]
            },
            'hairdresser': {
                'locations': [str(loc[0]) for loc in db.session.query(Hairdresser.location)
                            .filter(Hairdresser.location.isnot(None))
                            .filter(Hairdresser.approval_status == 'approved')
                            .distinct().all()],
                'providers': [str(name[0]) for name in db.session.query(Hairdresser.username)
                            .filter(Hairdresser.approval_status == 'approved')
                            .distinct().all()]
            },
            'makeupartist': {
                'locations': [str(loc[0]) for loc in db.session.query(Makeupartist.location)
                            .filter(Makeupartist.location.isnot(None))
                            .filter(Makeupartist.approval_status == 'approved')
                            .distinct().all()],
                'providers': [str(name[0]) for name in db.session.query(Makeupartist.username)
                            .filter(Makeupartist.approval_status == 'approved')
                            .distinct().all()]
            },
            'weddingplanner': {
                'locations': [str(loc[0]) for loc in db.session.query(Weddingplanner.location)
                            .filter(Weddingplanner.location.isnot(None))
                            .filter(Weddingplanner.approval_status == 'approved')
                            .distinct().all()],
                'providers': [str(name[0]) for name in db.session.query(Weddingplanner.username)
                            .filter(Weddingplanner.approval_status == 'approved')
                            .distinct().all()]
            }
        }
        
        # Sort locations and provider names for each service type
        for service_type in service_data:
            service_data[service_type]['locations'].sort()
            service_data[service_type]['providers'].sort()
        
        # Create locations_by_service dictionary for the template
        locations_by_service = {
            service_type: data['locations']
            for service_type, data in service_data.items()
        }
        
        return render_template("home_page.html", 
                             service_data=service_data,
                             locations_by_service=locations_by_service)
    except Exception as e:
        print(f"Error in home route: {str(e)}")
        return render_template("home_page.html", 
                             service_data={},
                             locations_by_service={})

@app.route("/booking")
@app.route("/booking/<service_type>/<int:service_id>")
def booking(service_type=None, service_id=None):
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Get service details if service_id is provided
    service = None
    if service_id:
        if service_type == 'venue':
            service = Venue.query.get(service_id)
        elif service_type == 'makeupartist':
            service = Makeupartist.query.get(service_id)
        elif service_type == 'hairdresser':
            service = Hairdresser.query.get(service_id)
        elif service_type == 'weddingplanner':
            service = Weddingplanner.query.get(service_id)
        
        if not service:
            return redirect(url_for('services'))
    
    return render_template("booking.html", service=service, service_type=service_type, datetime=datetime, timedelta=timedelta)

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
    query = config['model'].query.filter_by(approval_status='approved')
    
    # Apply filters from query parameters
    location = request.args.get('location')
    provider_name = request.args.get('provider')
    max_price = request.args.get('max_price')
    date = request.args.get('date')
    
    if location:
        query = query.filter(config['model'].location == location)
    if provider_name:
        query = query.filter(config['model'].username == provider_name)
    if max_price:
        query = query.filter(config['model'].price <= float(max_price))
    
    services_data = query.all()
    
    # Get all unique provider names and locations for this service type
    provider_names = [name[0] for name in db.session.query(config['model'].username)
                     .filter(config['model'].approval_status == 'approved')
                     .distinct().all()]
    locations = [loc[0] for loc in db.session.query(config['model'].location)
                .filter(config['model'].location.isnot(None))
                .filter(config['model'].approval_status == 'approved')
                .distinct().all()]
    
    return render_template("services.html", 
                         services=services_data, 
                         service_type=service_type,
                         title=config['title'],
                         provider_names=sorted(provider_names),
                         locations=sorted(locations),
                         selected_location=location,
                         selected_provider=provider_name)

@app.route("/api/services/<service_type>")  # API endpoint for dynamic loading
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


# Detail routes
@app.route('/service_details/<service_type>/<string:name>')
def service_details(service_type, name):
    if service_type not in SERVICE_CONFIG:
        return "Service type not found", 404
    
    config = SERVICE_CONFIG[service_type]
    service = config['model'].query.filter_by(username=name).first()
    
    if service:
        # Convert service object to a dictionary with only the needed attributes
        service_data = {
            'id': service.id,
            'username': service.username,
            'description': service.description or "",
            'location': service.location or "",
            'price': service.price or 0,
            'media': service.media or ""
        }
        # Get all images for this service
        images = ServiceImage.query.filter_by(service_type=service_type, service_id=service.id).all()
        image_filenames = [img.filename for img in images]
        
        return render_template('service_details.html', 
                             service=service_data,
                             service_type=service_type,
                             images=image_filenames)
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
        session['password']=user.password
        session['role'] = role  # Store the user's role in the session
        
        # Redirect based on role
        if role == "admin":
            return jsonify({"result": "success", "redirect": url_for('admin_dashboard')})
        elif role in ["venue", "hair_dresser", "makeup_artist", "wedding_planner"]:
            return jsonify({"result": "success", "redirect": url_for('provider_dashboard')})
        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "Invalid username or password"}), 401

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

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
        filename = secure_filename(media_file.filename)
        save_path = os.path.join('static', 'images', filename)
        media_file.save(save_path)
        media_path = f'{filename}'

    try:
        # Use the right model based on role
        if select_value == "user":
            new_user = User(
                username=username,
                password=password,
                email=email,
                phone_number=phone_number
            )
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"success": True, "message": "User registered successfully"})
            
        # Service provider registration
        new_provider = None
        if select_value == "venue":
            new_provider = Venue(
                username=username,
                password=password,
                phone_number=phone_number,
                description=description,
                location=location,
                price=price,
                media=media_path,
                email=email
            )
        elif select_value == "hair_dresser":
            new_provider = Hairdresser(
                username=username,
                password=password,
                phone_number=phone_number,
                description=description,
                location=location,
                price=price,
                media=media_path,
                email=email
            )
        elif select_value == "makeup_artist":
            new_provider = Makeupartist(
                username=username,
                password=password,
                phone_number=phone_number,
                description=description,
                location=location,
                price=price,
                media=media_path,
                email=email
            )
        elif select_value == "wedding_planner":
            new_provider = Weddingplanner(
                username=username,
                password=password,
                phone_number=phone_number,
                description=description,
                price=price,
                media=media_path,
                email=email
            )
        
        if new_provider:
            db.session.add(new_provider)
            db.session.commit()
            
            # Send notification to manager
            send_manager_notification_email(select_value, new_provider)
            
            return jsonify({
                "success": True, 
                "message": "Registration submitted successfully. Please wait for admin approval."
            })
        
        return jsonify({"success": False, "message": "Invalid role"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error: {str(e)}"})


#booking

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
        service_type = request.form.get('service_type')
        service_id = int(request.form.get('service_id'))
        booking_date = request.form.get('date')
        
        # Validate service exists based on type
        service = None
        if service_type == 'venue':
            service = Venue.query.get(service_id)
        elif service_type == 'makeupartist':
            service = Makeupartist.query.get(service_id)
        elif service_type == 'hairdresser':
            service = Hairdresser.query.get(service_id)
        elif service_type == 'weddingplanner':
            service = Weddingplanner.query.get(service_id)
        
        if not service:
            return jsonify({"success": False, "message": f"{service_type.title()} not found"}), 404
        
        # Convert string date to date object
        booking_date_obj = datetime.strptime(booking_date, '%Y-%m-%d').date()
        
        # Check if service is already booked on this date
        existing_booking = Booking.query.filter_by(
            service_type=service_type,
            service_id=service_id,
            booking_date=booking_date_obj
        ).filter(Booking.status != 'cancelled').first()
        
        if existing_booking:
            return jsonify({
                "success": False, 
                "message": f"Sorry, this {service_type} is already booked on the selected date"
            }), 400
        
        # Create booking with pending status
        booking = Booking(
            user_id=user.id,
            service_type=service_type,
            service_id=service_id,
            booking_date=booking_date_obj,
            status='pending'  # Explicitly set status to pending
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Send pending notification email to user
        email_sent = send_booking_pending_email(booking, user, service)
        
        # Send notification to service provider
        provider_notified = send_provider_booking_notification(booking, user, service)
        
        response_message = f"Booking request submitted successfully! Your booking ID is {booking.id}. Please wait for the provider's approval."
        if not email_sent and user.email:
            response_message += " (Note: There was an issue sending the confirmation email)"
        if not provider_notified and service.email:
            response_message += " (Note: There was an issue notifying the service provider)"
        
        return jsonify({
            "success": True, 
            "message": response_message,
            "booking_id": booking.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False, 
            "message": f"Error creating booking: {str(e)}"
        }), 500

@app.route('/check_service_availability', methods=['POST'])
def check_service_availability():
    """Check if a service is available on a specific date"""
    try:
        data = request.get_json()
        service_type = data.get('service_type')
        service_id = int(data.get('service_id'))
        booking_date = data.get('date')
        
        # Validate service exists based on type
        service = None
        if service_type == 'venue':
            service = Venue.query.get(service_id)
        elif service_type == 'makeupartist':
            service = Makeupartist.query.get(service_id)
        elif service_type == 'hairdresser':
            service = Hairdresser.query.get(service_id)
        elif service_type == 'weddingplanner':
            service = Weddingplanner.query.get(service_id)
        
        if not service:
            return jsonify({"available": False, "error": f"{service_type.title()} not found"}), 404
        
        # Convert string date to date object
        booking_date_obj = datetime.strptime(booking_date, '%Y-%m-%d').date()
        
        # Check for existing bookings (excluding cancelled ones)
        existing_booking = Booking.query.filter_by(
            service_type=service_type,
            service_id=service_id,
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
    
    bookings = Booking.query.filter_by(user_id=user.id)\
        .options(
            joinedload(Booking.venue_service),
            joinedload(Booking.makeupartist_service),
            joinedload(Booking.hairdresser_service),
            joinedload(Booking.weddingplanner_service)
        )\
        .order_by(Booking.created_at.desc()).all()
    return render_template('my_bookings.html', bookings=bookings)

@app.route('/test_email')
def test_email():
    try:
        msg = Message(
            'Test Email from Wedding Services',
            recipients=['ali2107767@miuegypt.edu.eg']
        )
        msg.body = 'This is a test email to verify the email configuration is working.'
        mail.send(msg)
        return "Test email sent successfully! Check your inbox."
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print("Error sending test email:")
        print(error_details)
        return f"Error sending test email: {str(e)}"






# emailssss functions
def send_manager_notification_email(service_type, provider):
    """Send notification email to manager about new service provider registration"""
    try:
        msg = Message(
            f'New {service_type.title()} Registration Requires Approval',
            recipients=['ali2107767@miuegypt.edu.eg']  # Manager's email
        )
        
        msg.html = render_template(
            'email/manager_notification.html',
            service_type=service_type,
            provider=provider
        )
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending manager notification: {str(e)}")
        return False

def send_provider_notification_email(provider, service_type, status):
    """Send notification email to provider about their registration status"""
    try:
        msg = Message(
            f'Your {service_type.title()} Registration Status',
            recipients=[provider.email]
        )
        
        msg.html = render_template(
            'email/provider_notification.html',
            provider=provider,
            service_type=service_type,
            status=status
        )
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending provider notification: {str(e)}")
        return False

def send_booking_pending_email(booking, user, service):
    """Send a pending booking notification email to the user"""
    try:
        if not user.email:
            print("User has no email address")
            return False
            
        msg = Message(
            'Your Booking Request - Pending Provider Approval',
            recipients=[user.email]
        )
        
        msg.html = render_template(
            'email/booking_pending.html',
            booking=booking,
            user=user,
            service=service
        )
        
        mail.send(msg)
        print(f"Pending booking email sent to {user.email}")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_provider_booking_notification(booking, user, service):
    """Send a booking notification email to the service provider"""
    try:
        if not service.email:
            print("Service provider has no email address")
            return False
            
        msg = Message(
            'New Booking Notification',
            recipients=[service.email]
        )
        
        msg.html = render_template(
            'email/provider_booking_notification.html',
            booking=booking,
            user=user,
            service=service
        )
        
        mail.send(msg)
        print(f"Booking notification email sent to provider {service.email}")
        return True
    except Exception as e:
        print(f"Error sending provider booking notification: {str(e)}")
        return False

def send_provider_update_notification(update, provider):
    """Send notification email to admin about provider update request"""
    try:
        msg = Message(
            f'Provider Update Request Requires Approval',
            recipients=['ali2107767@miuegypt.edu.eg']  # Admin's email
        )
        
        msg.html = render_template(
            'email/provider_update_notification.html',
            update=update,
            provider=provider
        )
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending provider update notification: {str(e)}")
        return False

def send_booking_status_update_email(booking, user, service, status):
    """Send an email to the user about their booking status update"""
    try:
        if not user.email:
            print("User has no email address")
            return False
            
        msg = Message(
            f'Your Booking Status Update - {status.title()}',
            recipients=[user.email]
        )
        
        msg.html = render_template(
            'email/booking_status_update.html',
            booking=booking,
            user=user,
            service=service,
            status=status
        )
        
        mail.send(msg)
        print(f"Booking status update email sent to {user.email}")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_review_request_email(booking, user, service):
    """Send an email to request a review after service completion"""
    try:
        msg = Message(
            'Please Review Your Wedding Service',
            recipients=[user.email]
        )
        
        msg.html = render_template(
            'email/review_request.html',
            booking=booking,
            user=user,
            service=service,
            review_link=url_for('submit_review', booking_id=booking.id, _external=True)
        )
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending review request email: {str(e)}")
        return False

def send_provider_cancellation_email(booking, user, service, reason='', contact=''):
    """Send a cancellation notification email to the service provider, including reason and contact."""
    try:
        if not service.email:
            print("Service provider has no email address")
            return False
        msg = Message(
            'Booking Cancelled Notification',
            recipients=[service.email]
        )
        msg.html = render_template(
            'email/provider_cancellation_notification.html',
            booking=booking,
            user=user,
            service=service,
            reason=reason,
            contact=contact
        )
        mail.send(msg)
        print(f"Cancellation email sent to provider {service.email}")
        return True
    except Exception as e:
        print(f"Error sending provider cancellation email: {str(e)}")
        return False





# admin
@app.route('/admin/dashboard')
def admin_dashboard():
    
    if 'username' not in session or not Admin.query.filter_by(username=session['username']).first():
        return redirect(url_for('login'))
    
    # Get all pending service providers
    pending_providers = {
        'venue': Venue.query.filter_by(approval_status='pending').all(),
        'makeupartist': Makeupartist.query.filter_by(approval_status='pending').all(),
        'hairdresser': Hairdresser.query.filter_by(approval_status='pending').all(),
        'weddingplanner': Weddingplanner.query.filter_by(approval_status='pending').all()
    }
    
    return render_template('admin_dashboard.html', pending_providers=pending_providers)

@app.route('/admin/approve_provider/<service_type>/<int:provider_id>')
def approve_provider(service_type, provider_id):
    if 'username' not in session or not Admin.query.filter_by(username=session['username']).first():
        return redirect(url_for('login'))
    
    try:
        # Get the provider based on service type
        provider = None
        if service_type == 'venue':
            provider = Venue.query.get(provider_id)
        elif service_type == 'makeupartist':
            provider = Makeupartist.query.get(provider_id)
        elif service_type == 'hairdresser':
            provider = Hairdresser.query.get(provider_id)
        elif service_type == 'weddingplanner':
            provider = Weddingplanner.query.get(provider_id)
        
        if not provider:
            return "Provider not found", 404
        
        provider.approval_status = 'approved'
        db.session.commit()
        
        # Send approval email to provider
        send_provider_notification_email(provider, service_type, 'approved')
        
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}", 500

@app.route('/admin/reject_provider/<service_type>/<int:provider_id>')
def reject_provider(service_type, provider_id):
    if 'username' not in session or not Admin.query.filter_by(username=session['username']).first():
        return redirect(url_for('login'))
    
    try:
        # Get the provider based on service type
        provider = None
        if service_type == 'venue':
            provider = Venue.query.get(provider_id)
        elif service_type == 'makeupartist':
            provider = Makeupartist.query.get(provider_id)
        elif service_type == 'hairdresser':
            provider = Hairdresser.query.get(provider_id)
        elif service_type == 'weddingplanner':
            provider = Weddingplanner.query.get(provider_id)
        
        if not provider:
            return "Provider not found", 404
        
        provider.approval_status = 'rejected'
        db.session.commit()
        
        # Send rejection email to provider
        send_provider_notification_email(provider, service_type, 'rejected')
        
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}", 500

@app.route('/admin/create_admin', methods=['POST'])
def create_admin():
    # Check if the current user is logged in and is an admin
    if 'username' not in session:
        return jsonify({"success": False, "message": "Please log in first"}), 401
    
    current_admin = Admin.query.filter_by(username=session['username']).first()
    if not current_admin:
        return jsonify({"success": False, "message": "Only admins can create new admin accounts"}), 403
    
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        phone_number = data.get('phone_number')
        
        # Validate required fields
        if not all([username, password]):
            return jsonify({"success": False, "message": "Username and password are required"}), 400
        
        # Check if username already exists
        if Admin.query.filter_by(username=username).first():
            return jsonify({"success": False, "message": "Username already exists"}), 400
        
        # Create new admin
        new_admin = Admin(
            username=username,
            password=password,
            email=email,
            phone_number=phone_number
        )
        
        db.session.add(new_admin)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "New admin account created successfully"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error creating admin account: {str(e)}"
        }), 500


# provider_dashboard

@app.route('/provider/profile')
def provider_profile():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    
    provider_type = session['role']
    if provider_type not in ['venue', 'hair_dresser', 'makeup_artist', 'wedding_planner']:
        return "Access denied", 403
    
    # Map provider types to models
    provider_models = {
        'venue': Venue,
        'hair_dresser': Hairdresser,
        'makeup_artist': Makeupartist,
        'wedding_planner': Weddingplanner
    }
    
    provider = provider_models[provider_type].query.filter_by(username=session['username']).first()
    if not provider:
        return "Provider not found", 404
    
    # Check for pending updates
    pending_update = ProviderUpdate.query.filter_by(
        provider_type=provider_type,
        provider_id=provider.id,
        status='pending'
    ).first()
    
    return render_template('provider_profile.html',
                         provider=provider,
                         provider_type=provider_type,
                         pending_update=pending_update)

@app.route('/provider/update', methods=['POST'])
def update_provider_profile():
    if 'username' not in session or 'role' not in session:
        return jsonify({"success": False, "message": "Please log in first"}), 401
    
    provider_type = session['role']
    if provider_type not in ['venue', 'hair_dresser', 'makeup_artist', 'wedding_planner']:
        return jsonify({"success": False, "message": "Access denied"}), 403
    
    try:
        # Get the provider
        provider_models = {
            'venue': Venue,
            'hair_dresser': Hairdresser,
            'makeup_artist': Makeupartist,
            'wedding_planner': Weddingplanner
        }
        provider = provider_models[provider_type].query.filter_by(username=session['username']).first()
        if not provider:
            return jsonify({"success": False, "message": "Provider not found"}), 404
        
        # Check if there's already a pending update
        existing_update = ProviderUpdate.query.filter_by(
            provider_type=provider_type,
            provider_id=provider.id,
            status='pending'
        ).first()
        if existing_update:
            return jsonify({
                "success": False,
                "message": "You already have pending changes awaiting approval"
            }), 400
        
        # Handle media file
        media_path = None
        if 'media' in request.files and request.files['media'].filename:
            media_file = request.files['media']
            filename = secure_filename(media_file.filename)
            save_path = os.path.join('static', 'images', 'pending_' + filename)
            media_file.save(save_path)
            media_path = filename
        
        # Create update request
        update = ProviderUpdate(
            provider_type=provider_type,
            provider_id=provider.id,
            email=request.form.get('email'),
            phone_number=request.form.get('phone_number'),
            description=request.form.get('description'),
            location=request.form.get('location'),
            price=float(request.form.get('price')),
            media=media_path
        )
        
        db.session.add(update)
        db.session.commit()
        
        # Notify admin
        send_provider_update_notification(update, provider)
        
        return jsonify({
            "success": True,
            "message": "Your changes have been submitted for admin approval"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error updating profile: {str(e)}"
        }), 500


@app.route('/provider/dashboard')
def provider_dashboard():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    
    # Map login roles to service types in database
    role_to_service_type = {
        'venue': 'venue',
        'hair_dresser': 'hairdresser',
        'makeup_artist': 'makeupartist',
        'wedding_planner': 'weddingplanner'
    }
    
    provider_type = session['role']
    if provider_type not in role_to_service_type:
        return "Access denied", 403
    
    # Map provider types to models
    provider_models = {
        'venue': Venue,
        'hair_dresser': Hairdresser,
        'makeup_artist': Makeupartist,
        'wedding_planner': Weddingplanner
    }
    
    provider = provider_models[provider_type].query.filter_by(username=session['username']).first()
    if not provider:
        return "Provider not found", 404
    
    # Get the correct service type for database queries
    service_type = role_to_service_type[provider_type]
    
    # Get upcoming bookings (future dates)
    upcoming_bookings = Booking.query.filter(
        Booking.service_type == service_type,
        Booking.service_id == provider.id,
        Booking.booking_date >= datetime.now().date(),
        Booking.status != 'cancelled'
    ).order_by(Booking.booking_date).limit(5).all()
    
    # Get recent bookings (all statuses)
    recent_bookings = Booking.query.filter(
        Booking.service_type == service_type,
        Booking.service_id == provider.id
    ).order_by(Booking.created_at.desc()).limit(5).all()
    
    # Calculate statistics
    total_bookings = Booking.query.filter(
        Booking.service_type == service_type,
        Booking.service_id == provider.id
    ).count()
    
    upcoming_count = Booking.query.filter(
        Booking.service_type == service_type,
        Booking.service_id == provider.id,
        Booking.booking_date >= datetime.now().date(),
        Booking.status != 'cancelled'
    ).count()
    
    completed_count = Booking.query.filter(
        Booking.service_type == service_type,
        Booking.service_id == provider.id,
        Booking.status == 'completed'
    ).count()
    
    # Check for pending updates
    pending_update = ProviderUpdate.query.filter_by(
        provider_type=provider_type,
        provider_id=provider.id,
        status='pending'
    ).first()
    
    stats = {
        'total_bookings': total_bookings,
        'upcoming_bookings': upcoming_count,
        'completed_bookings': completed_count
    }
    
    return render_template('provider_dashboard.html',
                         provider=provider,
                         upcoming_bookings=upcoming_bookings,
                         recent_bookings=recent_bookings,
                         stats=stats,
                         pending_update=pending_update)

@app.route('/provider/booking/<int:booking_id>/<string:action>', methods=['POST'])
def update_booking_status(booking_id, action):
    if 'username' not in session or 'role' not in session:
        return jsonify({"success": False, "message": "Please log in first"}), 401
    
    # Map login roles to service types in database
    role_to_service_type = {
        'venue': 'venue',
        'hair_dresser': 'hairdresser',
        'makeup_artist': 'makeupartist',
        'wedding_planner': 'weddingplanner'
    }
    
    provider_type = session['role']
    if provider_type not in role_to_service_type:
        return jsonify({"success": False, "message": "Access denied"}), 403
    
    try:
        # Get the booking
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({"success": False, "message": "Booking not found"}), 404
        
        # Get the correct service type for database queries
        service_type = role_to_service_type[provider_type]
        
        # Verify this booking belongs to the logged-in provider
        provider_models = {
            'venue': Venue,
            'hair_dresser': Hairdresser,
            'makeup_artist': Makeupartist,
            'wedding_planner': Weddingplanner
        }
        
        provider = provider_models[provider_type].query.filter_by(username=session['username']).first()
        if not provider or booking.service_id != provider.id or booking.service_type != service_type:
            return jsonify({"success": False, "message": "Access denied"}), 403
        
        # Update booking status based on action
        if action == 'approve':
            booking.status = 'confirmed'
            status_message = "Booking approved successfully"
        elif action == 'decline':
            booking.status = 'rejected'
            status_message = "Booking declined successfully"
        elif action == 'complete':
            booking.status = 'completed'
            status_message = "Booking marked as completed"
        else:
            return jsonify({"success": False, "message": "Invalid action"}), 400
        
        db.session.commit()
        
        # Get user and send email notification
        user = User.query.get(booking.user_id)
        if user:
            send_booking_status_update_email(booking, user, provider, booking.status)
        
        # If booking is marked as completed, send review request email
        if action == 'complete' and booking.status == 'completed':
            service = None
            if booking.service_type == 'venue':
                service = Venue.query.get(booking.service_id)
            elif booking.service_type == 'hairdresser':
                service = Hairdresser.query.get(booking.service_id)
            elif booking.service_type == 'makeupartist':
                service = Makeupartist.query.get(booking.service_id)
            elif booking.service_type == 'weddingplanner':
                service = Weddingplanner.query.get(booking.service_id)
            
            if user and service:
                send_review_request_email(booking, user, service)
        
        return jsonify({
            "success": True,
            "message": status_message,
            "new_status": booking.status
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error updating booking: {str(e)}"
        }), 500

@app.route('/admin/provider_updates')
def admin_provider_updates():
    if 'username' not in session or not Admin.query.filter_by(username=session['username']).first():
        return redirect(url_for('login'))
    
    # Get all pending provider updates
    updates = ProviderUpdate.query.filter_by(status='pending').order_by(ProviderUpdate.submitted_at.desc()).all()
    return render_template('admin_provider_updates.html', updates=updates)

@app.route('/admin/approve_provider_update/<int:update_id>')
def approve_provider_update(update_id):
    if 'username' not in session or not Admin.query.filter_by(username=session['username']).first():
        return redirect(url_for('login'))
    
    try:
        update = ProviderUpdate.query.get(update_id)
        if not update:
            return "Update not found", 404
        
        # Get the provider
        provider_models = {
            'venue': Venue,
            'hair_dresser': Hairdresser,
            'makeup_artist': Makeupartist,
            'wedding_planner': Weddingplanner
        }
        
        provider = provider_models[update.provider_type].query.get(update.provider_id)
        if not provider:
            return "Provider not found", 404
        
        # Update provider information
        provider.email = update.email
        provider.phone_number = update.phone_number
        provider.description = update.description
        if update.location:
            provider.location = update.location
        provider.price = update.price
        
        # Handle media update
        if update.media:
            # Move the pending image to permanent storage
            old_path = os.path.join('static', 'images', 'pending_' + update.media)
            new_path = os.path.join('static', 'images', update.media)
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
            provider.media = update.media
        
        # Mark update as approved
        update.status = 'approved'
        db.session.commit()
        
        # Send notification to provider
        send_provider_notification_email(provider, update.provider_type, 'approved')
        
        return redirect(url_for('admin_provider_updates'))
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}", 500

@app.route('/admin/reject_provider_update/<int:update_id>')
def reject_provider_update(update_id):
    if 'username' not in session or not Admin.query.filter_by(username=session['username']).first():
        return redirect(url_for('login'))
    
    try:
        update = ProviderUpdate.query.get(update_id)
        if not update:
            return "Update not found", 404
        
        # Get the provider
        provider_models = {
            'venue': Venue,
            'hair_dresser': Hairdresser,
            'makeup_artist': Makeupartist,
            'wedding_planner': Weddingplanner
        }
        
        provider = provider_models[update.provider_type].query.get(update.provider_id)
        if not provider:
            return "Provider not found", 404
        
        # Delete pending media if exists
        if update.media:
            pending_path = os.path.join('static', 'images', 'pending_' + update.media)
            if os.path.exists(pending_path):
                os.remove(pending_path)
        
        # Mark update as rejected
        update.status = 'rejected'
        db.session.commit()
        
        # Send notification to provider
        send_provider_notification_email(provider, update.provider_type, 'rejected')
        
        return redirect(url_for('admin_provider_updates'))
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}", 500

@app.route('/submit_review/<int:booking_id>', methods=['GET', 'POST'])
def submit_review(booking_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    booking = Booking.query.get_or_404(booking_id)
    user = User.query.filter_by(username=session['username']).first()
    
    # Verify this booking belongs to the logged-in user
    if booking.user_id != user.id:
        return "Access denied", 403
    
    # Check if review already exists
    existing_review = Review.query.filter_by(booking_id=booking_id).first()
    if existing_review:
        flash('You have already submitted a review for this booking', 'warning')
        return redirect(url_for('my_bookings'))
    
    if request.method == 'POST':
        try:
            rating = int(request.form.get('rating'))
            review_text = request.form.get('review_text')
            
            if not 1 <= rating <= 5:
                raise ValueError("Rating must be between 1 and 5")
            
            review = Review(
                booking_id=booking_id,
                user_id=user.id,
                service_type=booking.service_type,
                service_id=booking.service_id,
                rating=rating,
                review_text=review_text
            )
            
            db.session.add(review)
            db.session.commit()
            
            flash('Thank you for your review!', 'success')
            return redirect(url_for('service_details', 
                                  service_type=booking.service_type,
                                  name=booking.service.username))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting review: {str(e)}', 'error')
    
    return render_template('submit_review.html', booking=booking)

@app.route('/api/reviews/<service_type>/<int:service_id>')
def get_service_reviews(service_type, service_id):
    """API endpoint to get reviews for a service"""
    reviews = Review.query.filter_by(
        service_type=service_type,
        
        service_id=service_id
    ).order_by(Review.created_at.desc()).all()
    
    reviews_data = []
    for review in reviews:
        reviews_data.append({
            'username': review.user.username,
            'rating': review.rating,
            'review_text': review.review_text,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(reviews_data)

@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'username' not in session:
        return jsonify({"success": False, "message": "Please log in first"}), 401
    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({"success": False, "message": "Booking not found"}), 404
        user = User.query.filter_by(username=session['username']).first()
        if not user or booking.user_id != user.id:
            return jsonify({"success": False, "message": "Access denied"}), 403
        if booking.status == 'cancelled':
            return jsonify({"success": False, "message": "Booking already cancelled"}), 400
        data = request.get_json() or {}
        reason = data.get('reason', '')
        contact = data.get('contact', '')
        booking.status = 'cancelled'
        db.session.commit()
        # Notify provider of cancellation
        service = None
        if booking.service_type == 'venue':
            service = Venue.query.get(booking.service_id)
        elif booking.service_type == 'hairdresser':
            service = Hairdresser.query.get(booking.service_id)
        elif booking.service_type == 'makeupartist':
            service = Makeupartist.query.get(booking.service_id)
        elif booking.service_type == 'weddingplanner':
            service = Weddingplanner.query.get(booking.service_id)
        if service:
            send_provider_cancellation_email(booking, user, service, reason, contact)
        return jsonify({"success": True, "message": "Booking cancelled successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error cancelling booking: {str(e)}"}), 500

@app.route('/provider/images', methods=['GET', 'POST', 'DELETE'])
def provider_images():
    if 'username' not in session or 'role' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'}), 401
    provider_type = session['role']
    # Use the same mapping as in provider_dashboard and service_details
    role_to_service_type = {
        'venue': 'venue',
        'hair_dresser': 'hairdresser',
        'makeup_artist': 'makeupartist',
        'wedding_planner': 'weddingplanner'
    }
    provider_models = {
        'venue': Venue,
        'hair_dresser': Hairdresser,
        'makeup_artist': Makeupartist,
        'wedding_planner': Weddingplanner
    }
    if provider_type not in provider_models:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    provider = provider_models[provider_type].query.filter_by(username=session['username']).first()
    if not provider:
        return jsonify({'success': False, 'message': 'Provider not found'}), 404
    service_type = role_to_service_type[provider_type]
    if request.method == 'GET':
        images = ServiceImage.query.filter_by(service_type=service_type, service_id=provider.id).all()
        return jsonify({'images': [img.filename for img in images]})
    elif request.method == 'POST':
        if 'images' not in request.files:
            return jsonify({'success': False, 'message': 'No images uploaded'}), 400
        files = request.files.getlist('images')
        saved_files = []
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                save_path = os.path.join('static', 'images', 'edit images', filename)
                file.save(save_path)
                img = ServiceImage(service_type=service_type, service_id=provider.id, filename=filename)
                db.session.add(img)
                saved_files.append(filename)
        db.session.commit()
        return jsonify({'success': True, 'uploaded': saved_files})
    elif request.method == 'DELETE':
        data = request.get_json()
        filename = data.get('filename')
        img = ServiceImage.query.filter_by(service_type=service_type, service_id=provider.id, filename=filename).first()
        if not img:
            return jsonify({'success': False, 'message': 'Image not found'}), 404
        db.session.delete(img)
        db.session.commit()
        # Remove file from filesystem
        file_path = os.path.join('static', 'images', 'edit images', filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'success': True, 'deleted': filename})

if __name__ == '__main__':
    app.run(debug=True, port=5001)