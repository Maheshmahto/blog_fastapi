from fastapi import FastAPI
from database import engine
from models import Base
from routers import blog
import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Simple Blog App")
app.include_router(auth.router)
app.include_router(blog.router)


