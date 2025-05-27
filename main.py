from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from models import db, User, Admin, Venue, Makeupartist, Weddingplanner, Hairdresser, Venuedetails, Booking, ProviderUpdate
from datetime import datetime, timedelta
from sqlalchemy.orm import foreign, remote, joinedload
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.secret_key = "your_secret_key"

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ali2107767@miuegypt.edu.eg'
app.config['MAIL_PASSWORD'] = 'etbc flpx vuem pwks'
app.config['MAIL_DEFAULT_SENDER'] = ('Wedding Services', 'ali2107767@miuegypt.edu.eg')
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEBUG'] = True

# Initialize extensions
db.init_app(app)
mail = Mail(app)

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
    services_data = config['model'].query.filter_by(approval_status='approved').all()
    
    return render_template("services.html", 
                         services=services_data, 
                         service_type=service_type,
                         title=config['title'])

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
        
        # Create booking
        booking = Booking(
            user_id=user.id,
            service_type=service_type,
            service_id=service_id,
            booking_date=booking_date_obj
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Send confirmation email to user
        email_sent = send_booking_confirmation_email(booking, user, service)
        
        # Send notification to service provider
        provider_notified = send_provider_booking_notification(booking, user, service)
        
        response_message = f"Booking created successfully! Your booking ID is {booking.id}"
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

def send_booking_confirmation_email(booking, user, service):
    """Send a booking confirmation email to the user"""
    try:
        if not user.email:
            print("User has no email address")
            return False
            
        msg = Message(
            'Your Wedding Service Booking Confirmation',
            recipients=[user.email]
        )
        
        msg.html = render_template(
            'email/booking_confirmation.html',
            booking=booking,
            user=user,
            service=service
        )
        
        mail.send(msg)
        print(f"Confirmation email sent to {user.email}")
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
    
    # Get upcoming bookings (future dates)
    upcoming_bookings = Booking.query.filter(
        Booking.service_type == provider_type,
        Booking.service_id == provider.id,
        Booking.booking_date >= datetime.now().date(),
        Booking.status != 'cancelled'
    ).order_by(Booking.booking_date).limit(5).all()
    
    # Get recent bookings (all statuses)
    recent_bookings = Booking.query.filter(
        Booking.service_type == provider_type,
        Booking.service_id == provider.id
    ).order_by(Booking.created_at.desc()).limit(5).all()
    
    # Calculate statistics
    total_bookings = Booking.query.filter(
        Booking.service_type == provider_type,
        Booking.service_id == provider.id
    ).count()
    
    upcoming_count = Booking.query.filter(
        Booking.service_type == provider_type,
        Booking.service_id == provider.id,
        Booking.booking_date >= datetime.now().date(),
        Booking.status != 'cancelled'
    ).count()
    
    completed_count = Booking.query.filter(
        Booking.service_type == provider_type,
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

if __name__ == '__main__':
    app.run(debug=True, port=5001)