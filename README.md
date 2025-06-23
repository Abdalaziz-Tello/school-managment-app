# Noah Eco System - School Management System

A FastAPI-based school management system with role-based access control for administrators, teachers, parents, and bus mentors.

## Features

- **Role-based Authentication**: Admin, Teacher, Parent, and Bus Mentor roles
- **Student Management**: Track students, classes, and attendance
- **Activity Management**: Homework and activity submissions
- **Bus Tracking**: Real-time bus location tracking
- **Real-time Communication**: WebSocket support for live updates
- **RESTful API**: Complete API documentation with Swagger UI

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **Authentication**: JWT tokens
- **Real-time**: WebSockets
- **Deployment**: Render

## Local Development

### Prerequisites

- Python 3.9+
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd noah_eco_system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   export ADMIN_PASSWORD="your_admin_password"
   export SECRET_KEY="your_secret_key"
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Default Admin Credentials

- **Username**: admin
- **Password**: admin (or the value set in ADMIN_PASSWORD environment variable)

## Deployment on Render

### Method 1: Using render.yaml (Recommended)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file
   - Click "Apply" to deploy

### Method 2: Manual Deployment

1. **Create a new Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure the service**
   - **Name**: noah-eco-system
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variables**
   - `ADMIN_PASSWORD`: Your admin password
   - `SECRET_KEY`: A secure secret key

4. **Deploy**
   - Click "Create Web Service"

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ADMIN_PASSWORD` | Admin user password | Yes |
| `SECRET_KEY` | JWT secret key | Yes |

## API Documentation

Once deployed, access the API documentation at:
- **Swagger UI**: `https://your-app-name.onrender.com/docs`
- **ReDoc**: `https://your-app-name.onrender.com/redoc`

## Database

The application uses SQLite for both local development and production. The database file is stored at `./data/school.db` and is automatically created when the application starts.

## Project Structure

```
noah_eco_system/
├── app/
│   ├── core/           # Core functionality (auth, security, etc.)
│   ├── models/         # Database models
│   ├── routers/        # API routes
│   ├── schemas/        # Pydantic schemas
│   ├── database.py     # Database configuration
│   ├── main.py         # FastAPI application
│   └── init_db.py      # Database initialization
├── alembic/            # Database migrations
├── data/               # SQLite database
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment config
├── Procfile           # Alternative deployment config
└── runtime.txt        # Python version specification
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. 