from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import secrets
import string

from ..database import get_db
from ..models import models
from ..schemas import schemas
from ..core.auth import get_password_hash
from ..core.auth import get_current_user
from ..core.sms import sms_gateway

router = APIRouter(prefix="/admin", tags=["admin"])

def verify_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can perform this action"
        )
    return current_user

def generate_password(length: int = 12) -> str:
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@router.post("/users/teacher", response_model=schemas.UserCreationResponse)
async def create_teacher(
    user: schemas.UserCreate,
    current_user: models.User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Create a new teacher account."""
    # Generate random password if not provided
    if not user.password:
        user.password = generate_password()
    
    db_user = models.User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        phone_number=user.phone_number,
        role="teacher"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Send credentials via SMS
    sms_gateway.send_credentials(user.phone_number, user.username, user.password)
    
    # Return user with password for admin reference
    response_user = schemas.User(
        id=db_user.id,
        username=db_user.username,
        phone_number=db_user.phone_number,
        role=db_user.role,
        is_active=db_user.is_active
    )
    
    return {
        "user": response_user,
        "generated_password": user.password,
        "message": "Teacher created successfully. Password has been sent via SMS."
    }

@router.post("/users/parent", response_model=schemas.UserCreationResponse)
async def create_parent(
    user: schemas.UserCreate,
    current_user: models.User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Create a new parent account."""
    # Generate random password if not provided
    if not user.password:
        user.password = generate_password()
    
    db_user = models.User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        phone_number=user.phone_number,
        role="parent"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Send credentials via SMS
    sms_gateway.send_credentials(user.phone_number, user.username, user.password)
    
    # Return user with password for admin reference
    response_user = schemas.User(
        id=db_user.id,
        username=db_user.username,
        phone_number=db_user.phone_number,
        role=db_user.role,
        is_active=db_user.is_active
    )
    
    return {
        "user": response_user,
        "generated_password": user.password,
        "message": "Parent created successfully. Password has been sent via SMS."
    }

@router.post("/users/bus-mentor", response_model=schemas.UserCreationResponse)
async def create_bus_mentor(
    user: schemas.UserCreate,
    current_user: models.User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Create a new bus mentor account."""
    # Generate random password if not provided
    if not user.password:
        user.password = generate_password()
    
    db_user = models.User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        phone_number=user.phone_number,
        role="bus_mentor"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Send credentials via SMS
    sms_gateway.send_credentials(user.phone_number, user.username, user.password)
    
    # Return user with password for admin reference
    response_user = schemas.User(
        id=db_user.id,
        username=db_user.username,
        phone_number=db_user.phone_number,
        role=db_user.role,
        is_active=db_user.is_active
    )
    
    return {
        "user": response_user,
        "generated_password": user.password,
        "message": "Bus mentor created successfully. Password has been sent via SMS."
    }

@router.post("/classes", response_model=schemas.Class)
async def create_class(
    class_: schemas.ClassCreate,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin)
):
    """Create a new class and assign it to a teacher."""
    # Verify teacher exists
    teacher = db.query(models.User).filter(
        models.User.id == class_.teacher_id,
        models.User.role == "teacher"
    ).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    db_class = models.Class(**class_.dict())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

@router.post("/students", response_model=schemas.Student)
async def create_student(
    student: schemas.StudentCreate,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin)
):
    """Create a new student and assign them to a class."""
    # Verify class exists
    class_ = db.query(models.Class).filter(models.Class.id == student.class_id).first()
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )

    # Verify parent exists
    parent = db.query(models.User).filter(
        models.User.id == student.parent_id,
        models.User.role == "parent"
    ).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent not found"
        )

    db_student = models.Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@router.post("/send-credentials/{user_id}")
async def send_user_credentials(
    user_id: int,
    current_user: models.User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Trigger sending credentials via SMS for a specific user."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Generate new password
    new_password = generate_password()
    user.hashed_password = get_password_hash(new_password)
    db.commit()

    # Send via SMS
    success = sms_gateway.send_credentials(user.phone_number, user.username, new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send credentials via SMS"
        )
    
    return {"message": "Credentials sent successfully"}

@router.get("/users/teachers", response_model=List[schemas.User])
async def get_all_teachers(
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin)
):
    """Get all teacher accounts."""
    teachers = db.query(models.User).filter(models.User.role == "teacher").all()
    return teachers

@router.get("/users/parents", response_model=List[schemas.User])
async def get_all_parents(
    current_user: models.User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get all parent accounts."""
    parents = db.query(models.User).filter(models.User.role == "parent").all()
    return parents

@router.get("/users/bus-mentors", response_model=List[schemas.User])
async def get_all_bus_mentors(
    current_user: models.User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get all bus mentor accounts."""
    bus_mentors = db.query(models.User).filter(models.User.role == "bus_mentor").all()
    return bus_mentors

@router.get("/students", response_model=List[schemas.Student])
async def get_all_students(
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin)
):
    """Get all students."""
    students = db.query(models.Student).all()
    return students

@router.get("/classes", response_model=List[schemas.Class])
async def get_all_classes(
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin)
):
    """Get all classes."""
    classes = db.query(models.Class).all()
    return classes

@router.patch("/students/{student_id}/fees", response_model=schemas.Student)
async def update_student_fees(
    student_id: int,
    fees: schemas.StudentFeesUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin)
):
    """Update student fees."""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    student.fees = fees.fees
    db.commit()
    db.refresh(student)
    return student

@router.patch("/classes/{class_id}/teacher", response_model=schemas.Class)
async def update_class_teacher(
    class_id: int,
    teacher_update: schemas.ClassTeacherUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin)
):
    """Update class teacher."""
    class_ = db.query(models.Class).filter(models.Class.id == class_id).first()
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )
    
    teacher = db.query(models.User).filter(
        models.User.id == teacher_update.teacher_id,
        models.User.role == "teacher"
    ).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    class_.teacher_id = teacher_update.teacher_id
    db.commit()
    db.refresh(class_)
    return class_

@router.patch("/students/{student_id}/class", response_model=schemas.Student)
async def update_student_class(
    student_id: int,
    class_update: schemas.StudentClassUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin)
):
    """Update student's class."""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    class_ = db.query(models.Class).filter(models.Class.id == class_update.class_id).first()
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )
    
    student.class_id = class_update.class_id
    db.commit()
    db.refresh(student)
    return student 