from datetime import date

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from lib.database.config import get_db
from lib.database.models import MealType, Meal
from lib.utils.DateUtils import get_dates
from lib.utils.UserUtils import get_user_from_token

userMealsRouter = APIRouter()
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
@userMealsRouter.post("/create_meal", status_code=201)
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


@userMealsRouter.get("/get_meals", status_code=200)
def get_meals(
        day: str,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
):
    try:
        # Get user from token
        user = get_user_from_token(token, db)

        start_of_day, end_of_day = get_dates(day)

        meals = db.query(Meal).filter(
            Meal.userUuid == user.uuid,
            Meal.date >= start_of_day,
            Meal.date <= end_of_day
        ).all()

        return meals

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
