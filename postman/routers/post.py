from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db
import oauth2
from sqlalchemy import func
import schemas,utils,models,oauth2
from sqlalchemy.orm import Session
from typing import List
from database import get_db

router = APIRouter(
    prefix="/posts",tags=["Posts"]
)

@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), limit: int = 10, skip: int = 0,
              search: str = "",
              current_user: models.User = Depends(oauth2.get_current_user)):

    results = db.query(
        models.Post, 
        func.count(models.Vote.post_id).label("votes")
    ).join(
        models.Vote, 
        models.Vote.post_id == models.Post.id, 
        isouter=True  # LEFT JOIN so posts with 0 votes still show up
    ).filter(
        models.Post.title.contains(search)  # 2. Apply your search filter
    ).group_by(
        models.Post.id  # 3. Group by post so the count works correctly per post
    ).limit(
        limit  # 4. Apply pagination limit
    ).offset(
        skip   # 5. Apply pagination offset/skip
    ).all()
        
    return results  

@router.post("/",status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post_data: schemas.PostCreate,current_user: models.User = Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    new_post = models.Post(owner_id=current_user.id, **post_data.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/latest")
def get_latest_post(db: Session = Depends(get_db),current_user: models.User = Depends(oauth2.get_current_user)):
    latest_post = (
        db.query(models.Post)
        .order_by(models.Post.id.desc())
        .first()
    )
    return latest_post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_post(id: int, db: Session = Depends(get_db),current_user: models.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found",
        )
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User with id {current_user.id} is not authorized to delete this post",
        )
    db.delete(post)
    db.commit()
    return None

@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post_data: schemas.PostCreate , db: Session = Depends(get_db),current_user: models.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found",
        )
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User with id {current_user.id} is not authorized to update this post",
        )
    for field, value in post_data.model_dump().items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)
    return post

@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db),current_user: models.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found",
        )
    votes = db.query(func.count(models.Vote.post_id)).filter(
        models.Vote.post_id == id
    ).scalar()
    return {"Post": post, "votes": votes}
