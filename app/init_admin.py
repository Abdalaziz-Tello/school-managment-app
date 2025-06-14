import os
from sqlalchemy.orm import Session

from database import engine, Base, SessionLocal
from models.models import User
from core.security import get_password_hash

def init_admin():
    """Initialize the admin user with credentials from environment variables."""
    required_env_vars = ["ADMIN_USERNAME", "ADMIN_PASSWORD", "ADMIN_PHONE"]
    
    # Check for required environment variables
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print("Error: The following environment variables are required:")
        for var in missing_vars:
            print(f"- {var}")
        return False

    # Get credentials from environment
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin_phone = os.getenv("ADMIN_PHONE")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.username == admin_username).first()
        if admin:
            print(f"Admin user '{admin_username}' already exists.")
            return False

        # Create admin user
        admin = User(
            username=admin_username,
            hashed_password=get_password_hash(admin_password),
            phone_number=admin_phone,
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        print(f"Admin user '{admin_username}' created successfully!")
        return True
    
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing admin user...")
    success = init_admin()
    if success:
        print("""
Admin user initialized successfully!
You can now login using:
- Route: POST /login
- Body: {
    "username": "<ADMIN_USERNAME environment variable value>",
    "password": "<ADMIN_PASSWORD environment variable value>"
}
        """)
    else:
        print("Failed to initialize admin user. Please check the error messages above.") 