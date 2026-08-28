from app.db.database import Base, engine
from app.models.session import Session
from app.models.message import Message

Base.metadata.create_all(bind=engine)

print("Database tables created!")