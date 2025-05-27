from main import app, Admin, db

def create_admin_user():
    with app.app_context():
        # Check if admin already exists
        admin = Admin.query.filter_by(username='admin').first()
        if admin:
            print("Admin user already exists!")
            return
        
        # Create new admin user
        admin = Admin(
            username='admin',
            password='admin123',
            email='ali2107767@miuegypt.edu.eg',
            phone_number='123456789'
        )
        
        try:
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
            print("Username: admin")
            print("Password: admin123")
        except Exception as e:
            print("Error creating admin:", e)
            db.session.rollback()

if __name__ == '__main__':
    create_admin_user() 