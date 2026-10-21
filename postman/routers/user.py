from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db
import schemas,utils,models
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/users",tags=["Users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = utils.hash(user_data.password)
    
    # Unpack the dump and pass the hashed password directly
    user_dict = user_data.model_dump()
    user_dict["password"] = hashed_password
    
    user = models.User(**user_dict)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/{id}",response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found",
        )
    return user