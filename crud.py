from sqlalchemy.orm import Session
from models import Blog
from schemas import BlogCreate

def create_blog(db: Session, blog: BlogCreate, owner_id: int):
    new_blog = Blog(**blog.dict(), owner_id=owner_id)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


def get_blogs(db: Session):
    return db.query(Blog).all()

def get_blog(db: Session, blog_id: int):
    return db.query(Blog).filter(Blog.id == blog_id).first()

def delete_blog(db: Session, blog_id: int):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if blog:
        db.delete(blog)
        db.commit()
    return blog

def update_blog(db: Session, blog_id: int, blog_data: BlogCreate):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if blog:
        blog.title = blog_data.title
        blog.content = blog_data.content
        db.commit()
        db.refresh(blog)
    return blog
