
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("postgresql://attendance_db_93y7_user:yy7jHyEoEuV5z4B8JcdpGajMzjQSCITm@dpg-d668tmv5r7bs73cdmtlg-a/attendance_db_93y7")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
