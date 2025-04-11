from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import schemas, crud
from auth import verify_access_token

router = APIRouter(prefix="/blogs", tags=["Blogs"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.post("/", response_model=schemas.BlogOut)
def create_blog(
    blog: schemas.BlogCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_access_token)  
):
    return crud.create_blog(db, blog, owner_id=user_id)


@router.get("/", response_model=list[schemas.BlogOut])
def get_all_blogs(db: Session = Depends(get_db)):
    return crud.get_blogs(db)


@router.get("/{blog_id}", response_model=schemas.BlogOut)
def get_one_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = crud.get_blog(db, blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog


@router.delete("/{blog_id}")
def delete_blog(blog_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_blog(db, blog_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Blog not found")
    return {"detail": "Deleted successfully"}


@router.put("/{blog_id}", response_model=schemas.BlogOut)
def update_blog(blog_id: int, blog: schemas.BlogCreate, db: Session = Depends(get_db)):
    updated = crud.update_blog(db, blog_id, blog)
    if not updated:
        raise HTTPException(status_code=404, detail="Blog not found")
    return updated
