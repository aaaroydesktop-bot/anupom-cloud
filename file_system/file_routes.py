from fastapi import APIRouter, UploadFile, File, Request, Form, Depends, HTTPException
from fastapi.responses import FileResponse
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Message
from datetime import datetime, timedelta

from .file_service import save_file, get_file
import os

router = APIRouter()

SECRET_KEY = "anupom_secret_123"
ALGORITHM = "HS256"


# ---------------- DB SESSION ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- GET LOGGED USER ----------------
def get_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


# =====================================================
#                   SEND FILE
# =====================================================
@router.post("/send-file")
async def send_file(
    request: Request,
    receiver: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    sender = get_user(request)
    if not sender:
        raise HTTPException(status_code=401, detail="Login required")

    # Save file to disk
    stored_name = save_file(file, sender)

    # Save message to database
    msg = Message(
        sender=sender,
        receiver=receiver,
        file_name=stored_name,
        created_at=datetime.utcnow()   # VERY IMPORTANT
    )

    db.add(msg)
    db.commit()

    return {"status": "sent"}


# =====================================================
#                       INBOX
# =====================================================
@router.get("/inbox")
def inbox(request: Request, db: Session = Depends(get_db)):

    user = get_user(request)
    if not user:
        raise HTTPException(status_code=401)

    messages = db.query(Message).filter(Message.receiver == user).all()

    data = []

    for m in messages:

        # -------- FIX OLD DATABASE (created_at NULL) --------
        if m.created_at is None:
            m.created_at = datetime.utcnow()
            db.commit()

        # -------- SAFE FILENAME --------
        if "_" in m.file_name:
            filename = m.file_name.split("_", 1)[1]
        else:
            filename = m.file_name

        # -------- FILE TYPE DETECT --------
        ext = filename.split(".")[-1].lower()
        filetype = "other"

        if ext in ["png", "jpg", "jpeg", "gif", "webp"]:
            filetype = "image"
        elif ext in ["mp4", "webm", "mov"]:
            filetype = "video"
        elif ext == "pdf":
            filetype = "pdf"

        # -------- EXPIRY CALCULATION --------
        expire_date = m.created_at + timedelta(days=7)
        remaining_days = (expire_date - datetime.utcnow()).days

        if remaining_days < 0:
            remaining_days = 0

        data.append({
            "sender": m.sender,
            "file": filename,
            "type": filetype,
            "expires": remaining_days,
            "link": f"/download/{m.sender}/{m.file_name}"
        })

    return data


# =====================================================
#                     DOWNLOAD
# =====================================================
@router.get("/download/{sender}/{filename}")
def download(sender: str, filename: str):

    path = get_file(sender, filename)

    if not os.path.exists(path):
        raise HTTPException(status_code=404)

    # safe filename
    if "_" in filename:
        real = filename.split("_", 1)[1]
    else:
        real = filename

    return FileResponse(path, filename=real)


# =====================================================
#                     MY FILES
# =====================================================
@router.get("/my-files")
def my_files(request: Request, db: Session = Depends(get_db)):

    user = get_user(request)
    if not user:
        raise HTTPException(status_code=401)

    messages = db.query(Message).filter(Message.sender == user).all()

    data = []

    for m in messages:

        # safe filename
        if "_" in m.file_name:
            filename = m.file_name.split("_", 1)[1]
        else:
            filename = m.file_name

        ext = filename.split(".")[-1].lower()

        filetype = "other"
        if ext in ["png", "jpg", "jpeg", "gif", "webp"]:
            filetype = "image"
        elif ext in ["mp4", "webm", "mov"]:
            filetype = "video"
        elif ext == "pdf":
            filetype = "pdf"

        data.append({
            "receiver": m.receiver,
            "file": filename,
            "type": filetype,
            "link": f"/download/{m.sender}/{m.file_name}"
        })

    return data
