from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.database import Base

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    min_attendance = Column(Integer, default=75)

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    date = Column(Date)
    status = Column(String)
