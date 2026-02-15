from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import date

# ---------------- Students ----------------
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    # Relationship to attendance
    attendance = relationship("Attendance", back_populates="student")

# ---------------- Subjects ----------------
class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    min_attendance = Column(Integer, default=75)

    # Relationship to attendance
    attendance = relationship("Attendance", back_populates="subject")

# ---------------- Attendance ----------------
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    date = Column(Date, default=date.today)  # ✅ new column
    status = Column(String)


    # Relationships
    student = relationship("Student", back_populates="attendance")
    subject = relationship("Subject", back_populates="attendance")
