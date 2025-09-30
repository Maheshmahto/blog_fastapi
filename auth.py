from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
import schemas, models
from utils import hash_password, verify_password, send_email
from database import SessionLocal
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
import os
import secrets

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Auth header token dependency
security = HTTPBearer()

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create JWT Token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Signup endpoint
@router.post("/signup", response_model=schemas.UserOut)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = hash_password(user.password)
    new_user = models.User(email=user.email, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Login endpoint
@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"user_id": db_user.id})
    return {"access_token": token, "token_type": "bearer"}

# Protect routes using this
def verify_access_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")




@router.get("/protected-test", dependencies=[Depends(verify_access_token)])
def protected_route():
    return {"msg": "JWT Protected Route"}

@router.post("/forgot-password")
async def forgot_password(
    background_tasks: BackgroundTasks,
    user_email: schemas.ForgotPasswordSchema,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == user_email.email).first()
    if user:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)

        # Invalidate previous tokens
        existing_token = db.query(models.PasswordResetToken).filter_by(user_id=user.id).first()
        if existing_token:
            db.delete(existing_token)
            db.commit()

        reset_token = models.PasswordResetToken(
            user_id=user.id, token=token, expires_at=expires_at
        )
        db.add(reset_token)
        db.commit()

        reset_link = f"http://yourapp.com/reset-password?token={token}"
        background_tasks.add_task(
            send_email,
            email=user.email,
            subject="Password Reset Request",
            message=f"Click the link to reset your password: {reset_link}",
        )
    return {"msg": "If an account with that email exists, a password reset link has been sent."}


@router.post("/reset-password")
def reset_password(
    payload: schemas.ResetPasswordSchema, db: Session = Depends(get_db)
):
    token_record = (
        db.query(models.PasswordResetToken)
        .filter(models.PasswordResetToken.token == payload.token)
        .first()
    )

    if not token_record or token_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(models.User).filter(models.User.id == token_record.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = hash_password(payload.password)
    db.delete(token_record)
    db.commit()

    return {"msg": "Password has been reset successfully."}
