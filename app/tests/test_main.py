from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
import json

from ..main import app
from ..database import Base, get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_read_main():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "School Management System API"

def test_login():
    """Test login endpoint."""
    response = client.post(
        "/login",
        json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 401  # Should fail with invalid credentials

def test_protected_endpoint_without_token():
    """Test accessing protected endpoint without token."""
    response = client.get("/teacher/classes", params={"teacher_id": 1})
    assert response.status_code == 401  # Should fail without token

def test_protected_endpoint_with_invalid_token():
    """Test accessing protected endpoint with invalid token."""
    response = client.get(
        "/teacher/classes",
        headers={"Authorization": "Bearer invalid_token"},
        params={"teacher_id": 1}
    )
    assert response.status_code == 401  # Should fail with invalid token

@pytest.fixture(autouse=True)
def setup_database():
    """Create test database tables before each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine) 