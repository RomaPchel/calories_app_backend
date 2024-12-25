import uuid
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
    weight: float
    mealType: str
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
        print(user)
        new_meal = Meal(
            userUuid=user.uuid,
            uuid=str(uuid.uuid4()),
            title=meal.title,
            weight=int(meal.weight),
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
        print(e)
        raise e
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@userMealsRouter.get("/meals", status_code=200)
def get_meals(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
):
    try:
        # Get user from token
        user = get_user_from_token(token, db)


        meals = db.query(Meal).filter(
            Meal.userUuid == user.uuid,

        ).all()

        return meals

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@userMealsRouter.delete("/meals/{uuid}")
def delete_meal(uuid: str, db: Session = Depends(get_db)):
    try:
        meal = db.query(Meal).filter(Meal.uuid == uuid).first()
        if not meal:
            raise HTTPException(status_code=404, detail="Meal not found")
        db.delete(meal)
        db.commit()
        return {"message": "Meal deleted successfully"}
    except HTTPException as e:
        print(e)
        raise e
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
