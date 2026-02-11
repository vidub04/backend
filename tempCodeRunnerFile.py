from app.database import engine
from app.models import Base

print("creating db")


Base.metadata.create_all(bind=engine)


print("db created")
