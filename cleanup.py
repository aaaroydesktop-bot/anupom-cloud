from database import SessionLocal
from models import Message
from datetime import datetime, timedelta
import os

UPLOAD_DIR = "uploads"

db = SessionLocal()

# 7 দিনের পুরোনো ফাইল খুঁজবো
expire_time = datetime.utcnow() - timedelta(days=7)

old_files = db.query(Message).filter(Message.created_at < expire_time).all()

deleted = 0

for file in old_files:
    file_path = os.path.join(UPLOAD_DIR, file.sender, file.file_name)

    # physical file delete
    if os.path.exists(file_path):
        os.remove(file_path)
        print("Deleted file:", file_path)
        deleted += 1

    # database entry delete
    db.delete(file)

db.commit()
db.close()

print("Cleanup complete. Total deleted:", deleted)

