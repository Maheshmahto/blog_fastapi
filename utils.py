from passlib.context import CryptContext
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
import os

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_TLS=os.getenv("MAIL_TLS").lower() == 'true',
    MAIL_SSL=os.getenv("MAIL_SSL").lower() == 'false',
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

#  Verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def send_email(email: str, subject: str, message: str):
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=message,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
