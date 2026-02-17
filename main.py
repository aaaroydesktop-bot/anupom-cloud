from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel

import random
import smtplib
from email.mime.text import MIMEText

from database import Base, engine, SessionLocal

from models import User


from file_system.file_routes import router as file_router

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


# ================= APP =================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")





Base.metadata.create_all(bind=engine)

# ================= SCHEMAS =================
class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class OTPVerify(BaseModel):
    username: str
    otp: str

class ForgotRequest(BaseModel):
    email: str

class ResetPassword(BaseModel):
    email: str
    otp: str
    new_password: str

# ================= AUTH =================
SECRET_KEY = "anupom_secret_123"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p):
    return pwd_context.hash(p)

def verify_password(p, h):
    return pwd_context.verify(p, h)

def create_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(days=1)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

@app.get("/me")
def get_me(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401)
    return {"email": user}

# ================= EMAIL OTP =================
def send_otp_email(to_email, otp):
    sender_email = "testanupom@gmail.com"
    sender_password = "dkmgqjujdkxjuwus"


    msg = MIMEText(f"""
    Hello 👋,

    Welcome to Anupom Cloud ☁️

    🔐 Your OTP Code: {otp}

    ⏳ This code will expire in 5 minutes.
    Please do NOT share this code with anyone.

    If you didn’t request this login,
    you can safely ignore this email.

    — Anupom Cloud Security Team 🛡️
    """)

    msg["Subject"] = "Verification OTP"
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print("MAIL ERROR:", e)
        raise HTTPException(status_code=500, detail="Email failed")

login_otp_storage = {}
reset_otp_storage = {}

# ================= PAGES =================
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/otp", response_class=HTMLResponse)
def otp_page(request: Request):
    return templates.TemplateResponse("otp.html", {"request": request})

@app.get("/forgot", response_class=HTMLResponse)
def forgot_page(request: Request):
    return templates.TemplateResponse("forgot.html", {"request": request})

@app.get("/reset", response_class=HTMLResponse)
def reset_page(request: Request):
    return templates.TemplateResponse("reset.html", {"request": request})

@app.get("/home", response_class=HTMLResponse)
def home_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

# ================= DB SESSION =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ================= REGISTER =================
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    db.add(User(email=user.email, password=hash_password(user.password)))
    db.commit()
    return {"message": "Registered Successfully"}

# ================= LOGIN =================
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.username).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Email not found")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Wrong password")

    otp = str(random.randint(100000, 999999))
    login_otp_storage[user.username] = otp
    send_otp_email(user.username, otp)

    return {"message": "OTP sent"}

# ================= VERIFY OTP =================
# ================= VERIFY OTP =================
@app.post("/verify-otp")
def verify_otp(data: OTPVerify):

    real = login_otp_storage.get(data.username)

    if not real or real != data.otp:
        raise HTTPException(status_code=401, detail="Invalid OTP")

    token = create_token({"sub": data.username})
    del login_otp_storage[data.username]

    response = JSONResponse({"message": "Login success"})

    # ⭐⭐⭐ আসল fix এখানে
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=36000,
        path="/"      # 🔥🔥🔥 এটা না থাকলেই তোমার bug হচ্ছিল
    )

    return response


# ================= FORGOT PASSWORD =================
@app.post("/forgot-password")
def forgot_password(data: ForgotRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")

    otp = str(random.randint(100000, 999999))
    reset_otp_storage[data.email] = otp

    send_otp_email(data.email, otp)

    return {"message": "Reset OTP sent"}

# ================= RESET PASSWORD =================
@app.post("/reset-password")
def reset_password(data: ResetPassword, db: Session = Depends(get_db)):

    real_otp = reset_otp_storage.get(data.email)

    if not real_otp or real_otp != data.otp:
        raise HTTPException(status_code=401, detail="Invalid OTP")

    user = db.query(User).filter(User.email == data.email).first()
    user.password = hash_password(data.new_password)

    db.commit()
    del reset_otp_storage[data.email]

    return {"message": "Password changed successfully"}


# ================= LOGOUT =================
@app.get("/logout")
def logout():
    response = RedirectResponse("/login")
    response.delete_cookie("access_token")
    return response


# ⭐⭐⭐⭐⭐ সবচেয়ে নিচে (LAST LINE)
app.include_router(file_router)


class MaxBodySizeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request._body = await request.body()
        return await call_next(request)

app.add_middleware(MaxBodySizeMiddleware)
