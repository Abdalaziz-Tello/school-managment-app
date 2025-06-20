from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import admin, teacher, parent, bus_mentor, auth, websocket
from .routers import admin_auth, teacher_auth, parent_auth, bus_mentor_auth
from .init_db import init_db

# Create database tables and initialize admin account
init_db()

app = FastAPI(
    title="School Management System API",
    description="A FastAPI backend for school management with role-based access control",
    version="1.0.0"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routers
app.include_router(auth.router)
app.include_router(admin_auth.router)
app.include_router(teacher_auth.router)
app.include_router(parent_auth.router)
app.include_router(bus_mentor_auth.router)

# Include feature routers
app.include_router(admin.router)
app.include_router(teacher.router)
app.include_router(parent.router)
app.include_router(bus_mentor.router)
app.include_router(websocket.router)

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "message": "School Management System API",
        "version": "1.0.0",
        "documentation": "/docs",
        "redoc": "/redoc"
    } 