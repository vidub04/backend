from app.database import engine,Base
from app.models import Subject, Attendance

print("creating db")


Base.metadata.create_all(bind=engine)


print("db created")
