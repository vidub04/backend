from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.database import SessionLocal, engine, Base
from app import models
from fastapi.middleware.cors import CORSMiddleware

#Drop all tables (only if you don’t need old data)
Base.metadata.drop_all(bind=engine)

#Recreate all tables based on updated models
Base.metadata.create_all(bind=engine)
print("Tables recreated")

app = FastAPI()




app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://attendance-main-frontend.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)








# ---------------- Database Dependency ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- Home ----------------
@app.get("/")
def home():
    return {"message": "Backend running"}

# ---------------- Subjects ----------------
@app.post("/subjects")
def add_subject(name: str, min_attendance: int = 75, db: Session = Depends(get_db)):
    subject = models.Subject(name=name, min_attendance=min_attendance)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject

@app.get("/subjects")
def get_subjects(db: Session = Depends(get_db)):
    return db.query(models.Subject).all()

# ---------------- Students ----------------
@app.post("/students")
def add_student(name: str, email: str, db: Session = Depends(get_db)):
    student = models.Student(name=name, email=email)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

@app.get("/students")
def get_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()

# ---------------- Attendance ----------------
@app.post("/attendance")
def mark_attendance(student_id: int, subject_id: int, status: str, db: Session = Depends(get_db)):
    # Validate student and subject
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not student or not subject:
        raise HTTPException(status_code=404, detail="Student or Subject not found")

    record = models.Attendance(
        student_id=student_id,
        subject_id=subject_id,
        date=date.today(),
        status=status.lower()  # "present" or "absent"
    )
    db.add(record)
    db.commit()
    return {"message": "Attendance marked"}

# ---------------- Subject-wise Attendance for a Student ----------------
@app.get("/attendance/subjectwise/{student_id}")
def subjectwise_attendance(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    subjects = db.query(models.Subject).all()
    result = []

    for subj in subjects:
        records = db.query(models.Attendance).filter(
            models.Attendance.student_id == student_id,
            models.Attendance.subject_id == subj.id
        ).all()
        total = len(records)
        present = len([r for r in records if r.status == "present"])
        percent = (present / total * 100) if total > 0 else 0
        result.append({
            "subject_id": subj.id,
            "subject_name": subj.name,
            "total_classes": total,
            "present": present,
            "percentage": round(percent, 2),
            "safe": percent >= subj.min_attendance
        })

    return {"student_id": student.id, "student_name": student.name, "subjects": result}

# ---------------- Overall Attendance for a Student ----------------
@app.get("/attendance/overall/{student_id}")
def overall_attendance(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    records = db.query(models.Attendance).filter(models.Attendance.student_id == student_id).all()
    total = len(records)
    present = len([r for r in records if r.status == "present"])
    percent = (present / total * 100) if total > 0 else 0

    return {
        "student_id": student.id,
        "student_name": student.name,
        "total_classes": total,
        "present": present,
        "overall_percentage": round(percent, 2),
        "safe": percent >= 75
    }

# ---------------- AI Attendance Advice ----------------
def attendance_advice(total, present):
    if total == 0:
        return "No classes yet"
    percent = (present / total) * 100
    if percent >= 75:
        return "You are safe. Maintain this attendance."
    else:
        required = 0
        while ((present + required) / (total + required)) * 100 < 75:
            required += 1
        return f"Attend next {required} classes continuously to reach 75%"

@app.get("/ai/advice/{student_id}")
def ai_advice(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    records = db.query(models.Attendance).filter(models.Attendance.student_id == student_id).all()
    total = len(records)
    present = len([r for r in records if r.status == "present"])
    advice = attendance_advice(total, present)
    return {
        "student_id": student.id,
        "student_name": student.name,
        "advice": advice
    }
