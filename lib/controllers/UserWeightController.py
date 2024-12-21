from datetime import date

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from lib.database.config import get_db
from lib.database.models import UserWeight
from lib.utils.DateUtils import get_dates
from lib.utils.UserUtils import get_user_from_token

userMacrosRouter = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Pydantic Model for adding weight
class UserWeightCreate(BaseModel):
    weight: float


class UserWeightResponse(BaseModel):
    userUuid: str
    weight: float
    date: str

    class Config:
        orm_mode = True


@userMacrosRouter.post("/add_weight", status_code=201)
def add_user_weight(weight: UserWeightCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        # Get user from token
        user = get_user_from_token(token, db)

        new_weight = UserWeight(
            userUuid=user.uuid,
            weight=weight.weight,
            date=date.today()
        )

        db.add(new_weight)
        db.commit()

        return {"message": "Weight added successfully", "data": weight.dict()}

    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@userMacrosRouter.get("/get_weights", response_model=list[UserWeightResponse])
def get_user_weights(
        day: str,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
):
    try:
        # Get user from token
        user = get_user_from_token(token, db)

        # Validate and parse the start_date and end_date if provided
        start_of_day, end_of_day = get_dates(day)

        weights = db.query(UserWeight).filter(
            UserWeight.userUuid == user.uuid,
            UserWeight.date >= start_of_day,
            UserWeight.date <= end_of_day
        ).all()

        return weights

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
