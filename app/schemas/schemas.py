from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# Base Models
class UserBase(BaseModel):
    username: str
    phone_number: str

class UserCreate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int
    role: str
    is_active: bool

    class Config:
        orm_mode = True

class ClassBase(BaseModel):
    name: str
    teacher_id: int

class ClassCreate(ClassBase):
    pass

class Class(ClassBase):
    id: int

    class Config:
        orm_mode = True

class StudentBase(BaseModel):
    name: str
    class_id: int
    parent_id: int
    profile_picture: Optional[str] = None
    fees: float = 0.0

class StudentCreate(StudentBase):
    """
    Schema for creating a new student.

    To upload a profile picture:
    1. Use a multipart/form-data request.
    2. Send the image file in a field named 'profile_picture'.
    3. The backend will upload the image to Cloudflare Images and store the returned URL in the profile_picture field.
    """
    pass

class Student(StudentBase):
    id: int

    class Config:
        orm_mode = True

class StudentFeesUpdate(BaseModel):
    fees: float

class StudentClassUpdate(BaseModel):
    class_id: int

class ActivityBase(BaseModel):
    title: str
    description: str
    due_date: datetime
    class_id: int
    is_homework: bool = False

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: int

    class Config:
        orm_mode = True

class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_homework: Optional[bool] = None

class ActivitySubmissionBase(BaseModel):
    activity_id: int
    student_id: int
    content: str

class ActivitySubmissionCreate(ActivitySubmissionBase):
    pass

class ActivitySubmission(ActivitySubmissionBase):
    id: int
    submission_date: datetime

    class Config:
        orm_mode = True

class AttendanceBase(BaseModel):
    student_id: int
    is_present: bool = True

class AttendanceCreate(AttendanceBase):
    pass

class Attendance(AttendanceBase):
    id: int
    date: datetime

    class Config:
        orm_mode = True

class CommentBase(BaseModel):
    student_id: int
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    teacher_id: int
    created_at: datetime
    is_read: bool

    class Config:
        orm_mode = True

class BusRecordBase(BaseModel):
    student_id: int
    location_lat: float
    location_lon: float
    status: str

class BusRecordCreate(BusRecordBase):
    pass

class BusRecord(BusRecordBase):
    id: int
    bus_mentor_id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class BusRouteUpdate(BaseModel):
    student_ids: List[int]
    location_lat: float
    location_lon: float
    status: str

# Token Schema
class TokenUser(BaseModel):
    id: int
    username: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: TokenUser

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# SMS Schema
class SMSRequest(BaseModel):
    phone_number: str
    message: str

class ClassTeacherUpdate(BaseModel):
    teacher_id: int

class UserLogin(BaseModel):
    username: str
    password: str 