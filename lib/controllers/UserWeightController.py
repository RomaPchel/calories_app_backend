from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from lib.database.config import get_db
from lib.database.models import UserWeight
from lib.utils.DateUtils import get_dates, parse_dates
from lib.utils.UserUtils import get_user_from_token

userWeightRouter = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Pydantic Model for adding weight
class UserWeightCreate(BaseModel):
    weight: float
    date: str


class UserWeightResponse(BaseModel):
    weight: float
    date: str

    class Config:
        orm_mode = True


@userWeightRouter.post("/add_weight", status_code=201)
def add_user_weight(weight: UserWeightCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        # Get user from token
        user = get_user_from_token(token, db)

        new_weight = UserWeight(
            userUuid=user.uuid,
            weight=weight.weight,
            date= datetime.strptime(weight.date, "%Y-%m-%d").date(),
        )

        db.add(new_weight)
        db.commit()

        return {"message": "Weight added successfully", "data": weight.dict()}

    except HTTPException as e:
        print(e)
        raise e
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@userWeightRouter.get("/weights", response_model=list[UserWeightResponse])
def get_user_weights(
        # start_date: Optional[str] = None,
        # end_date: Optional[str] = None,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
):
    try:
        # Get user from token
        user = get_user_from_token(token, db)

        # start_of_day, end_of_day = parse_dates(start_date, end_date)

        query = db.query(UserWeight).filter(UserWeight.userUuid == user.uuid)

        # if start_of_day and end_of_day:
        #     query = query.filter(start_of_day <= UserWeight.date <= end_of_day)
        # elif start_of_day:
        #     query = query.filter(UserWeight.date >= start_of_day)
        # elif end_of_day:
        #     query = query.filter(UserWeight.date <= end_of_day)

        weights = query.all()

        weights_response = [
            {"date": weight.date.isoformat(), "weight": weight.weight} for weight in weights
        ]

        return weights_response

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
