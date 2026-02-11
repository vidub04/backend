from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Backend running"}
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from app.models import Subject

@app.post("/subjects")
def add_subject(name: str, db: Session = Depends(get_db)):
    subject = Subject(name=name)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject

@app.get("/subjects")
def get_subjects(db: Session = Depends(get_db)):
    return db.query(Subject).all()
from datetime import date
from app.models import Attendance

@app.post("/attendance")
def mark_attendance(
    subject_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    record = Attendance(
        subject_id=subject_id,
        date=date.today(),
        status=status
    )
    db.add(record)
    db.commit()
    return {"message": "Attendance marked"}
@app.get("/attendance/summary/{subject_id}")
def attendance_summary(subject_id: int, db: Session = Depends(get_db)):
    records = db.query(Attendance).filter(
        Attendance.subject_id == subject_id
    ).all()

    total = len(records)
    present = len([r for r in records if r.status == "present"])

    percentage = (present / total) * 100 if total > 0 else 0

    return {
        "total_classes": total,
        "present": present,
        "percentage": round(percentage, 2),
        "safe": percentage >= 75
    }
@app.get("/attendance/overall")
def overall_attendance(db: Session = Depends(get_db)):
    records = db.query(Attendance).all()
    total = len(records)
    present = len([r for r in records if r.status == "present"])

    percent = (present / total) * 100 if total > 0 else 0

    return {
        "overall_percentage": round(percent, 2),
        "safe": percent >= 75
    }
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
@app.get("/ai/advice")
@app.get("/ai/advice")
def ai_advice(db: Session = Depends(get_db)):
    try:
        records = db.query(Attendance).all()

        total = len(records)
        present = sum(1 for r in records if r.status == "present")

        return attendance_advice(total, present)

    except Exception as e:
        print("AI ERROR 👉", e)
        return {"error": str(e)}



