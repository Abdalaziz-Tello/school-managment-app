from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from ..database import get_db
from ..models import models
from ..schemas import schemas
from ..core.auth import get_current_user

router = APIRouter(prefix="/bus-mentor", tags=["bus_mentor"])

def verify_bus_mentor(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "bus_mentor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only bus mentor users can perform this action"
        )
    return current_user

@router.post("/record", response_model=schemas.BusRecord)
async def record_student_bus_status(
    record: schemas.BusRecordCreate,
    current_user: models.User = Depends(verify_bus_mentor),
    db: Session = Depends(get_db)
):
    """Record a student's bus status (picked up or dropped off) with location."""
    # Verify student exists
    student = db.query(models.Student).filter(models.Student.id == record.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Verify status is valid
    if record.status not in ["picked_up", "dropped_off"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Must be 'picked_up' or 'dropped_off'"
        )

    db_record = models.BusRecord(
        **record.dict(),
        bus_mentor_id=current_user.id
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.get("/students", response_model=List[schemas.Student])
async def get_bus_route_students(
    current_user: models.User = Depends(verify_bus_mentor),
    db: Session = Depends(get_db)
):
    """Get all students assigned to this bus mentor's route."""
    # For simplicity, we'll just return all students
    # In a real system, you'd have a bus_route table and filter by route
    students = db.query(models.Student).all()
    return students

@router.get("/records/{date}", response_model=List[schemas.BusRecord])
async def get_daily_records(
    date: str,
    current_user: models.User = Depends(verify_bus_mentor),
    db: Session = Depends(get_db)
):
    """Get all bus records for a specific date."""
    try:
        record_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    records = (
        db.query(models.BusRecord)
        .filter(
            models.BusRecord.bus_mentor_id == current_user.id,
            models.BusRecord.timestamp >= record_date,
            models.BusRecord.timestamp < record_date + timedelta(days=1)
        )
        .all()
    )
    return records

@router.post("/attendance", response_model=schemas.Attendance)
async def mark_bus_attendance(
    attendance: schemas.AttendanceCreate,
    current_user: models.User = Depends(verify_bus_mentor),
    db: Session = Depends(get_db)
):
    """Mark attendance for a student when they board or leave the bus."""
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

@router.get("/route")
async def get_bus_route(
    current_user: models.User = Depends(verify_bus_mentor),
    db: Session = Depends(get_db)
):
    """Get bus route details including all students."""
    # Get all students assigned to this bus mentor
    students = db.query(models.Student).all()  # In a real system, filter by route
    
    # Get latest location for each student
    student_locations = []
    for student in students:
        latest_record = (
            db.query(models.BusRecord)
            .filter(models.BusRecord.student_id == student.id)
            .order_by(models.BusRecord.timestamp.desc())
            .first()
        )
        
        student_locations.append({
            "student_id": student.id,
            "student_name": student.name,
            "location": {
                "lat": latest_record.location_lat,
                "lon": latest_record.location_lon
            } if latest_record else None,
            "status": latest_record.status if latest_record else None
        })
    
    return {
        "bus_mentor_id": current_user.id,
        "students": student_locations
    }

@router.post("/route/update")
async def update_bus_route(
    route_update: schemas.BusRouteUpdate,
    current_user: models.User = Depends(verify_bus_mentor),
    db: Session = Depends(get_db)
):
    """Update bus route with new location."""
    # In a real system, you would update a bus_route table
    # For now, we'll just create a new bus record for each student
    for student_id in route_update.student_ids:
        student = db.query(models.Student).filter(models.Student.id == student_id).first()
        if student:
            record = models.BusRecord(
                student_id=student_id,
                bus_mentor_id=current_user.id,
                location_lat=route_update.location_lat,
                location_lon=route_update.location_lon,
                status=route_update.status
            )
            db.add(record)
    
    db.commit()
    return {"message": "Bus route updated successfully"} 