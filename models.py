from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base   # ⭐ এটা ছিল না — সবচেয়ে important

# ---------- USER TABLE ----------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)


# ---------- MESSAGE TABLE ----------

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String)
    receiver = Column(String)
    file_name = Column(String)

    # ⭐ IMPORTANT FIX
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)