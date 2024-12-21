from datetime import date

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from lib.database.config import get_db
from lib.database.models import UserMacros, UserOptions, Meal
from lib.utils.DateUtils import get_dates
from lib.utils.UserMacrosUtils import calculate_user_macros, calculate_water_intake
from lib.utils.UserUtils import get_user_from_token

userMacrosRouter = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserMacrosSchema(BaseModel):
    calories: int
    proteins: int
    carbs: int
    fats: int


@userMacrosRouter.post("/update-user_macros", status_code=201)
def update_user_macros(user_macros: UserMacrosSchema, db: Session = Depends(get_db),
                       token: str = Depends(oauth2_scheme)):
    try:
        print(token)

        # Get user from token
        user = get_user_from_token(token, db)

        # Check if user options already exist for this user
        existing_user_macros = db.query(UserMacros).filter(UserMacros.userUuid == user.uuid).first()
        if not existing_user_macros:
            raise HTTPException(status_code=400, detail="UserMacros not found for this user.")

        # Update the existing user macros
        existing_user_macros.gender = user_macros.calories
        existing_user_macros.height = user_macros.fats
        existing_user_macros.weight = user_macros.carbs
        existing_user_macros.weightGoal = user_macros.proteins

        # Commit changes to the database
        db.commit()
        db.refresh(existing_user_macros)

        return {"message": "UserMacros updated successfully", "data": user_macros.dict()}

    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@userMacrosRouter.get("/get-user-macros", status_code=200)
def get_user_macros(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        # Get user from token
        user = get_user_from_token(token, db)

        # Retrieve UserMacros for the user
        user_macros = db.query(UserMacros).filter(UserMacros.userUuid == user.uuid).first()
        if not user_macros:
            raise HTTPException(status_code=404, detail="UserMacros not found for this user.")

        # Return the retrieved UserMacros
        return {
            "message": "UserMacros retrieved successfully",
            "data": {
                "calories": user_macros.calories,
                "proteins": user_macros.proteins,
                "carbs": user_macros.carbs,
                "fats": user_macros.fats
            }
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@userMacrosRouter.get("/recommended-user-macros", status_code=200)
def recommended_user_macros(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        # Get user from token
        user = get_user_from_token(token, db)

        # Retrieve UserOptions for the user
        user_options = db.query(UserOptions).filter(UserOptions.userUuid == user.uuid).first()
        if not user_options:
            raise HTTPException(status_code=404, detail="UserOptions not found for this user.")

        # Calculate recommended macros using the provided function
        user_macros = calculate_user_macros(user, user_options)

        # Return the recommended macros
        return {
            "message": "Recommended UserMacros calculated successfully",
            "data": {
                "calories": user_macros.calories,
                "proteins": user_macros.proteins,
                "carbs": user_macros.carbs,
                "fats": user_macros.fats
            }
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@userMacrosRouter.get("/get_macros_by_day", status_code=200)
def get_macros_by_day(
        day: str,  # Date in 'YYYY-MM-DD' format
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
):
    try:
        # Get user from token
        user = get_user_from_token(token, db)

        start_of_day, end_of_day = get_dates(day)

        # Query meals for the specific day
        meals = db.query(Meal).filter(
            Meal.userUuid == user.uuid,
            Meal.date >= start_of_day,
            Meal.date <= end_of_day
        ).all()

        # Initialize totals
        total_calories = 0
        total_proteins = 0
        total_fats = 0
        total_carbs = 0

        # Sum up the values from the meals
        for meal in meals:
            total_calories += meal.calories
            total_proteins += meal.proteins
            total_fats += meal.fats
            total_carbs += meal.carbs

        # Return the total macros for the given day
        return {
            "date": day,
            "calories": total_calories,
            "proteins": total_proteins,
            "fats": total_fats,
            "carbs": total_carbs
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
