import os
from sqlalchemy.orm import Session

from .database import engine, Base, SessionLocal
from .models.models import User
from .core.auth import get_password_hash

def init_db():
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            # Create admin user
            admin_password = os.getenv("ADMIN_PASSWORD", "admin")  # Default password is "admin"
            admin = User(
                username="admin",
                hashed_password=get_password_hash(admin_password),
                phone_number="1234567890",  # Change in production
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("Admin user created successfully!")
            print(f"Username: admin")
            print(f"Password: {admin_password}")
        else:
            print("Admin user already exists.")
    
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialization completed.") 