from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from ..database import get_db
from ..models import models
from ..schemas import schemas
from ..core.auth import get_current_user

router = APIRouter(prefix="/teacher", tags=["teacher"])

def verify_teacher(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teacher users can perform this action"
        )
    return current_user

@router.get("/classes", response_model=List[schemas.Class])
async def get_teacher_classes(
    current_user: models.User = Depends(verify_teacher),
    db: Session = Depends(get_db)
):
    """Get all classes assigned to a teacher."""
    classes = db.query(models.Class).filter(models.Class.teacher_id == current_user.id).all()
    return classes

@router.post("/attendance", response_model=schemas.Attendance)
async def mark_attendance(
    attendance: schemas.AttendanceCreate,
    current_user: models.User = Depends(verify_teacher),
    db: Session = Depends(get_db)
):
    """Mark attendance for a student."""
    # Verify student exists
    student = db.query(models.Student).filter(models.Student.id == attendance.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    db_attendance = models.Attendance(**attendance.dict())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

@router.post("/activities", response_model=schemas.Activity)
async def create_activity(
    activity: schemas.ActivityCreate,
    current_user: models.User = Depends(verify_teacher),
    db: Session = Depends(get_db)
):
    """Create a new activity or homework for a class."""
    # Verify class exists and teacher is assigned to it
    class_ = db.query(models.Class).filter(
        models.Class.id == activity.class_id,
        models.Class.teacher_id == current_user.id
    ).first()
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found or you are not assigned to it"
        )

    db_activity = models.Activity(**activity.dict())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@router.get("/activities/{class_id}", response_model=List[schemas.Activity])
async def get_class_activities(
    class_id: int,
    current_user: models.User = Depends(verify_teacher),
    db: Session = Depends(get_db)
):
    """Get all activities for a specific class."""
    # Verify teacher is assigned to the class
    class_ = db.query(models.Class).filter(
        models.Class.id == class_id,
        models.Class.teacher_id == current_user.id
    ).first()
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found or you are not assigned to it"
        )

    activities = db.query(models.Activity).filter(models.Activity.class_id == class_id).all()
    return activities

@router.get("/attendance/{class_id}/{date}", response_model=List[schemas.Attendance])
async def get_class_attendance(
    class_id: int,
    date: str,
    current_user: models.User = Depends(verify_teacher),
    db: Session = Depends(get_db)
):
    """Get attendance records for a class on a specific date."""
    # Verify teacher is assigned to the class
    class_ = db.query(models.Class).filter(
        models.Class.id == class_id,
        models.Class.teacher_id == current_user.id
    ).first()
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found or you are not assigned to it"
        )

    try:
        attendance_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    attendance_records = (
        db.query(models.Attendance)
        .join(models.Student)
        .filter(
            models.Student.class_id == class_id,
            models.Attendance.date >= attendance_date,
            models.Attendance.date < attendance_date + timedelta(days=1)
        )
        .all()
    )
    return attendance_records

@router.post("/comments", response_model=schemas.Comment)
async def create_comment(
    comment: schemas.CommentCreate,
    current_user: models.User = Depends(verify_teacher),
    db: Session = Depends(get_db)
):
    """Send a comment to a student's parent."""
    # Verify student exists
    student = db.query(models.Student).filter(models.Student.id == comment.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    db_comment = models.Comment(
        **comment.dict(),
        teacher_id=current_user.id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/classes/{class_id}/students", response_model=List[schemas.Student])
async def get_class_students(
    class_id: int,
    current_user: models.User = Depends(verify_teacher),
    db: Session = Depends(get_db)
):
    """Get all students in a class."""
    # Verify teacher is assigned to the class
    class_ = db.query(models.Class).filter(
        models.Class.id == class_id,
        models.Class.teacher_id == current_user.id
    ).first()
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found or you are not assigned to it"
        )

    students = db.query(models.Student).filter(models.Student.class_id == class_id).all()
    return students

@router.put("/activities/{activity_id}", response_model=schemas.Activity)
async def update_activity(
    activity_id: int,
    activity_update: schemas.ActivityUpdate,
    current_user: models.User = Depends(verify_teacher),
    db: Session = Depends(get_db)
):
    """Update an activity or homework."""
    # Verify activity exists and teacher is assigned to the class
    activity = (
        db.query(models.Activity)
        .join(models.Class)
        .filter(
            models.Activity.id == activity_id,
            models.Class.teacher_id == current_user.id
        )
        .first()
    )
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found or you are not authorized to modify it"
        )

    for key, value in activity_update.dict(exclude_unset=True).items():
        setattr(activity, key, value)
    
    db.commit()
    db.refresh(activity)
    return activity

@router.delete("/activities/{activity_id}")
async def delete_activity(
    activity_id: int,
    current_user: models.User = Depends(verify_teacher),
    db: Session = Depends(get_db)
):
    """Delete an activity or homework."""
    # Verify activity exists and teacher is assigned to the class
    activity = (
        db.query(models.Activity)
        .join(models.Class)
        .filter(
            models.Activity.id == activity_id,
            models.Class.teacher_id == current_user.id
        )
        .first()
    )
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found or you are not authorized to delete it"
        )

    db.delete(activity)
    db.commit()
    return {"message": "Activity deleted successfully"} 