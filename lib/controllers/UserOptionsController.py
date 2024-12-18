from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from lib.database.config import get_db
from lib.database.models import UserOptions

router = APIRouter()

class UserOptionsSchema(BaseModel):
    userUuid: str
    gender: str
    height: str
    weight: str
    weightGoal: str
    goal: str
    activityLevel: str
    age: str

@router.post("/user-options", status_code=201)
def save_user_options(user_options: UserOptionsSchema, db: Session = Depends(get_db)):
    try:
        existing_user_options = db.query(UserOptions).filter(UserOptions.userUuid == user_options.userUuid).first()
        if existing_user_options:
            raise HTTPException(status_code=400, detail="UserOptions already exist for this user.")

        new_user_options = UserOptions(
            userUuid=user_options.userUuid,
            gender=user_options.gender,
            height=user_options.height,
            weight=user_options.weight,
            weightGoal=user_options.weightGoal,
            goal=user_options.goal,
            activityLevel=user_options.activityLevel,
            age=user_options.age
        )

        db.add(new_user_options)
        db.commit()
        db.refresh(new_user_options)

        return {"message": "UserOptions saved successfully", "data": user_options.dict()}

    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
