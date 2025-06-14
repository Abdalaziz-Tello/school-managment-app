# School Management System API

A FastAPI-based backend system for school management with role-based access control.

## Features

- Role-based authentication (Admin, Teacher, Parent, Bus Mentor)
- JWT-based authentication
- SQLite database
- Student attendance tracking
- Homework and activity management
- Bus tracking functionality
- SMS notification capability

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables for admin initialization:
```bash
# Linux/macOS
export ADMIN_USERNAME="your_admin_username"
export ADMIN_PASSWORD="your_secure_password"
export ADMIN_PHONE="your_phone_number"

# Windows (CMD)
set ADMIN_USERNAME=your_admin_username
set ADMIN_PASSWORD=your_secure_password
set ADMIN_PHONE=your_phone_number

# Windows (PowerShell)
$env:ADMIN_USERNAME="your_admin_username"
$env:ADMIN_PASSWORD="your_secure_password"
$env:ADMIN_PHONE="your_phone_number"
```

4. Initialize the admin user:
```bash
python app/init_admin.py
```

5. Start the application:
```bash
uvicorn app.main:app --reload
```

## Authentication

### Admin Login
1. Send a POST request to `/login` with the following body:
```json
{
    "username": "your_admin_username",
    "password": "your_admin_password"
}
```

2. The response will contain your JWT token:
```json
{
    "access_token": "your.jwt.token",
    "token_type": "bearer"
}
```

3. Include this token in all subsequent requests:
```
Authorization: Bearer your.jwt.token
```

### Other Users
All users (Admin, Teacher, Parent, Bus Mentor) use the same `/login` endpoint. The system automatically handles permissions based on the user's role.

## Docker Setup

1. Build the Docker image:
```bash
docker build -t school-management-api .
```

2. Run the container with environment variables:
```bash
docker run -d -p 8000:8000 \
  -e ADMIN_USERNAME=your_admin_username \
  -e ADMIN_PASSWORD=your_secure_password \
  -e ADMIN_PHONE=your_phone_number \
  school-management-api
```

## API Documentation

Once the application is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests using pytest:
```bash
pytest
```

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── init_admin.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── core/
│   └── tests/
├── requirements.txt
├── Dockerfile
└── README.md
```

## Security Notes

- Passwords are hashed using SHA-256
- JWT tokens expire after 30 minutes
- All sensitive operations require proper authentication
- Role-based access control is strictly enforced
- Admin credentials must be set via environment variables
- All API endpoints use proper authorization headers

## Environment Variables

Create a `.env` file with the following variables:
```
SECRET_KEY=your-secret-key
SMS_API_KEY=your-sms-api-key
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_password
ADMIN_PHONE=your_phone_number
``` 