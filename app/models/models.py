from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    phone_number = Column(String)
    role = Column(String)  # admin, teacher, parent, bus_mentor
    is_active = Column(Boolean, default=True)

    # Relationships
    teacher_classes = relationship("Class", back_populates="teacher")
    parent_students = relationship("Student", back_populates="parent")
    bus_mentor_records = relationship("BusRecord", back_populates="bus_mentor")
    teacher_comments = relationship("Comment", back_populates="teacher", foreign_keys="Comment.teacher_id")

class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    teacher = relationship("User", back_populates="teacher_classes")
    students = relationship("Student", back_populates="class_")
    activities = relationship("Activity", back_populates="class_")

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    profile_picture = Column(String, nullable=True)  # Make profile_picture optional
    fees = Column(Float)
    class_id = Column(Integer, ForeignKey("classes.id"))
    parent_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    class_ = relationship("Class", back_populates="students")
    parent = relationship("User", back_populates="parent_students")
    attendance_records = relationship("Attendance", back_populates="student")
    activity_submissions = relationship("ActivitySubmission", back_populates="student")
    bus_records = relationship("BusRecord", back_populates="student")
    comments = relationship("Comment", back_populates="student")

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    date = Column(DateTime, default=datetime.utcnow)
    is_present = Column(Boolean, default=False)

    # Relationships
    student = relationship("Student", back_populates="attendance_records")

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    due_date = Column(DateTime)
    class_id = Column(Integer, ForeignKey("classes.id"))
    is_homework = Column(Boolean, default=False)

    # Relationships
    class_ = relationship("Class", back_populates="activities")
    submissions = relationship("ActivitySubmission", back_populates="activity")

class ActivitySubmission(Base):
    __tablename__ = "activity_submissions"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    submission_date = Column(DateTime, default=datetime.utcnow)
    content = Column(String)

    # Relationships
    activity = relationship("Activity", back_populates="submissions")
    student = relationship("Student", back_populates="activity_submissions")

class BusRecord(Base):
    __tablename__ = "bus_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    bus_mentor_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    location_lat = Column(Float)
    location_lon = Column(Float)
    status = Column(String)  # "picked_up", "dropped_off"

    # Relationships
    student = relationship("Student", back_populates="bus_records")
    bus_mentor = relationship("User", back_populates="bus_mentor_records")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

    # Relationships
    student = relationship("Student", back_populates="comments")
    teacher = relationship("User", foreign_keys=[teacher_id]) 