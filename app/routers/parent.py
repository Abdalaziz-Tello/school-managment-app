from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from ..database import get_db
from ..models import models
from ..schemas import schemas
from ..core.auth import get_current_user

router = APIRouter(prefix="/parent", tags=["parent"])

def verify_parent(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only parent users can perform this action"
        )
    return current_user

@router.get("/students", response_model=List[schemas.Student])
async def get_parent_students(
    current_user: models.User = Depends(verify_parent),
    db: Session = Depends(get_db)
):
    """Get all students associated with a parent."""
    students = db.query(models.Student).filter(models.Student.parent_id == current_user.id).all()
    return students

@router.get("/attendance/{student_id}", response_model=List[schemas.Attendance])
async def get_student_attendance(
    student_id: int,
    start_date: str,
    end_date: str,
    current_user: models.User = Depends(verify_parent),
    db: Session = Depends(get_db)
):
    """Get attendance records for a student within a date range."""
    # Verify student belongs to parent
    student = db.query(models.Student).filter(
        models.Student.id == student_id,
        models.Student.parent_id == current_user.id
    ).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    attendance_records = (
        db.query(models.Attendance)
        .filter(
            models.Attendance.student_id == student_id,
            models.Attendance.date >= start,
            models.Attendance.date < end
        )
        .all()
    )
    return attendance_records

@router.get("/homework/{student_id}", response_model=List[schemas.Activity])
async def get_student_homework(
    student_id: int,
    current_user: models.User = Depends(verify_parent),
    db: Session = Depends(get_db)
):
    """Get all homework assignments for a student."""
    # Verify student belongs to parent
    student = db.query(models.Student).filter(
        models.Student.id == student_id,
        models.Student.parent_id == current_user.id
    ).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    homework = (
        db.query(models.Activity)
        .filter(
            models.Activity.class_id == student.class_id,
            models.Activity.is_homework == True
        )
        .all()
    )
    return homework

@router.get("/activities/{student_id}", response_model=List[schemas.Activity])
async def get_student_activities(
    student_id: int,
    current_user: models.User = Depends(verify_parent),
    db: Session = Depends(get_db)
):
    """Get all activities for a student."""
    # Verify student belongs to parent
    student = db.query(models.Student).filter(
        models.Student.id == student_id,
        models.Student.parent_id == current_user.id
    ).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    activities = (
        db.query(models.Activity)
        .filter(
            models.Activity.class_id == student.class_id,
            models.Activity.is_homework == False
        )
        .all()
    )
    return activities

@router.get("/bus-location/{student_id}")
async def get_student_bus_location(
    student_id: int,
    current_user: models.User = Depends(verify_parent),
    db: Session = Depends(get_db)
):
    """Get the latest bus location for a student."""
    # Verify student belongs to parent
    student = db.query(models.Student).filter(
        models.Student.id == student_id,
        models.Student.parent_id == current_user.id
    ).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    latest_record = (
        db.query(models.BusRecord)
        .filter(models.BusRecord.student_id == student_id)
        .order_by(models.BusRecord.timestamp.desc())
        .first()
    )
    
    if not latest_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No bus records found for this student"
        )
    
    return {
        "location": {
            "lat": latest_record.location_lat,
            "lon": latest_record.location_lon
        },
        "status": latest_record.status,
        "timestamp": latest_record.timestamp
    }

@router.get("/comments/{student_id}", response_model=List[schemas.Comment])
async def get_student_comments(
    student_id: int,
    current_user: models.User = Depends(verify_parent),
    db: Session = Depends(get_db)
):
    """Get all comments for a student."""
    # Verify student belongs to parent
    student = db.query(models.Student).filter(
        models.Student.id == student_id,
        models.Student.parent_id == current_user.id
    ).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    comments = db.query(models.Comment).filter(models.Comment.student_id == student_id).all()
    return comments

@router.get("/students/{student_id}/fees")
async def get_student_fees(
    student_id: int,
    current_user: models.User = Depends(verify_parent),
    db: Session = Depends(get_db)
):
    """Get student's fees information."""
    # Verify student belongs to parent
    student = db.query(models.Student).filter(
        models.Student.id == student_id,
        models.Student.parent_id == current_user.id
    ).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    return {
        "student_id": student.id,
        "student_name": student.name,
        "fees": student.fees
    }

@router.get("/students/{student_id}/class")
async def get_student_class_details(
    student_id: int,
    current_user: models.User = Depends(verify_parent),
    db: Session = Depends(get_db)
):
    """Get student's class details including teacher information."""
    # Verify student belongs to parent
    student = db.query(models.Student).filter(
        models.Student.id == student_id,
        models.Student.parent_id == current_user.id
    ).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    class_ = db.query(models.Class).filter(models.Class.id == student.class_id).first()
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )

    teacher = db.query(models.User).filter(models.User.id == class_.teacher_id).first()
    
    return {
        "class_id": class_.id,
        "class_name": class_.name,
        "teacher": {
            "id": teacher.id,
            "name": teacher.username,
            "phone": teacher.phone_number
        } if teacher else None
    } 