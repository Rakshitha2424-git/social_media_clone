from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import oauth2
import schemas

router = APIRouter(prefix="/vote", tags=["Vote"])


@router.get("/", response_model=List[int])
def get_my_votes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    votes = db.query(models.Vote.post_id).filter(
        models.Vote.user_id == current_user.id
    ).all()
    return [post_id for (post_id,) in votes]


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(
    vote_data: schemas.vote,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    post = db.query(models.Post).filter(
        models.Post.id == vote_data.post_id
    ).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {vote_data.post_id} does not exist",
        )

    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote_data.post_id,
        models.Vote.user_id == current_user.id,
    )
    found_vote = vote_query.first()

    if vote_data.dir == 1:
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"user {current_user.id} has already voted on post {vote_data.post_id}",
            )
        db.add(models.Vote(post_id=vote_data.post_id, user_id=current_user.id))
        db.commit()
        return {"message": "Successfully added vote"}

    if not found_vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vote does not exist",
        )
    vote_query.delete(synchronize_session=False)
    db.commit()
    return {"message": "Successfully deleted vote"}
