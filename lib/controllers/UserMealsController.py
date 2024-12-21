from datetime import datetime, date
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from lib.database.config import get_db
from lib.database.models import UserMacros, UserOptions, MealType, Meal
from lib.utils.DateUtils import get_dates
from lib.utils.UserMacrosUtils import calculate_user_macros, calculate_water_intake
from lib.utils.UserUtils import get_user_from_token

userMacrosRouter = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class MealCreate(BaseModel):
    title: str
    weight: int
    mealType: MealType
    calories: int
    proteins: int
    fats: int
    carbs: int

# Endpoint to create a meal with user inputted macros
@userMacrosRouter.post("/create_meal", status_code=201)
def create_meal(meal: MealCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        print(token)

        # Get user from token
        user = get_user_from_token(token, db)

        new_meal = Meal(
            uuid=user.uuid,
            title=meal.title,
            weight=meal.weight,
            mealType=meal.mealType,
            calories=meal.calories,
            proteins=meal.proteins,
            fats=meal.fats,
            carbs=meal.carbs,
            date=date.today()
        )

        db.add(new_meal)
        db.commit()

        return {"message": "UserMeal saved successfully", "data": meal.dict()}

    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@userMacrosRouter.get("/get_meals", status_code=200)
def get_meals(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        # Get user from token
        user = get_user_from_token(token, db)

        parsed_start_date, parsed_end_date = get_dates(start_date, end_date)

        if parsed_start_date and parsed_end_date:
            meals = db.query(Meal).filter(
                Meal.userUuid == user.uuid,
                Meal.date >= parsed_start_date,
                Meal.date <= parsed_end_date
            ).all()
        elif parsed_start_date:
            meals = db.query(Meal).filter(
                Meal.userUuid == user.uuid,
                Meal.date >= parsed_start_date
            ).all()
        elif parsed_end_date:
            meals = db.query(Meal).filter(
                Meal.userUuid == user.uuid,
                Meal.date <= parsed_end_date
            ).all()
        else:
            meals = db.query(Meal).filter(Meal.userUuid == user.uuid).all()

        if not meals:
            raise HTTPException(status_code=404, detail="No meals found")

        return meals

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")