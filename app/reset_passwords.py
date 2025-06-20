import os
from sqlalchemy.orm import Session

from .database import engine, Base, SessionLocal
from .models.models import User
from .core.auth import get_password_hash

def reset_passwords():
    """Reset passwords for all users to fix bcrypt compatibility issues."""
    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Reset admin password
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            admin_password = os.getenv("ADMIN_PASSWORD", "admin")
            admin.hashed_password = get_password_hash(admin_password)
            print(f"Admin password reset successfully!")
            print(f"Username: admin")
            print(f"Password: {admin_password}")
        else:
            # Create admin user if it doesn't exist
            admin_password = os.getenv("ADMIN_PASSWORD", "admin")
            admin = User(
                username="admin",
                hashed_password=get_password_hash(admin_password),
                phone_number="1234567890",
                role="admin",
                is_active=True
            )
            db.add(admin)
            print(f"Admin user created successfully!")
            print(f"Username: admin")
            print(f"Password: {admin_password}")
        
        # Reset passwords for all other users to a default password
        default_password = "password123"
        other_users = db.query(User).filter(User.username != "admin").all()
        
        for user in other_users:
            user.hashed_password = get_password_hash(default_password)
            print(f"Reset password for user: {user.username} to: {default_password}")
        
        db.commit()
        print(f"Reset passwords for {len(other_users)} users")
        print("All passwords have been reset successfully!")
        
    except Exception as e:
        print(f"Error resetting passwords: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Resetting passwords...")
    reset_passwords()
    print("Password reset completed.") 