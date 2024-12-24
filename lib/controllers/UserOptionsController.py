from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from lib.database.config import get_db
from lib.database.models import UserOptions, UserMacros, WeightGoal, ActivityLevel, Gender
from lib.utils.UserMacrosUtils import calculate_user_macros, calculate_user_intake
from lib.utils.UserUtils import get_user_from_token

userOptionsRouter = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserOptionsSchema(BaseModel):
    gender: str
    height: float
    weight: float
    weightGoal: str
    activityLevel: str
    age: int


@userOptionsRouter.post("/save-user-options", status_code=201)
def save_user_options(user_options: UserOptionsSchema, db: Session = Depends(get_db),
                      token: str = Depends(oauth2_scheme)):
    try:
        # Get user from token
        user = get_user_from_token(token, db)

        # Check if user options already exist for this user
        existing_user_options = db.query(UserOptions).filter(UserOptions.userUuid == user.uuid).first()
        if existing_user_options:
            raise HTTPException(status_code=400, detail="UserOptions already exist for this user.")

        intake = calculate_user_intake(user_options)
        # Create new user options
        new_user_options = UserOptions(
            userUuid=user.uuid,  # Use the UUID of the user from the database
            gender=user_options.gender,
            height=user_options.height,
            weight=user_options.weight,
            weightGoal=user_options.weightGoal,
            activityLevel=user_options.activityLevel,
            age=user_options.age,
            caloriesIntake=intake,
        )

        db.add(new_user_options)
        db.commit()
        db.refresh(new_user_options)

        user_macros = calculate_user_macros(user, user_options)

        saveOrUpdateUserMacros(db, user, user_macros)

        return {"message": "UserOptions saved successfully", "data": user_options.dict()}

    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@userOptionsRouter.post("/update-user-options", status_code=201)
def update_user_options(user_options: UserOptionsSchema, db: Session = Depends(get_db),
                      token: str = Depends(oauth2_scheme)):
    try:
        print(token)

        # Get user from token
        user = get_user_from_token(token, db)

        # Check if user options already exist for this user
        existing_user_options = db.query(UserOptions).filter(UserOptions.userUuid == user.uuid).first()
        if not existing_user_options:
            raise HTTPException(status_code=400, detail="UserOptions not found for this user.")

        # Update the existing user options
        existing_user_options.gender = user_options.gender
        existing_user_options.height = user_options.height
        existing_user_options.weight = user_options.weight
        existing_user_options.weightGoal = user_options.weightGoal
        existing_user_options.activityLevel = user_options.activityLevel
        existing_user_options.age = user_options.age

        # Commit changes to the database
        db.commit()
        db.refresh(existing_user_options)

        user_macros = calculate_user_macros(user, user_options)

        saveOrUpdateUserMacros(db, user, user_macros)

        return {"message": "UserOptions updated successfully", "data": user_options.dict()}

    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@userOptionsRouter.get("/get-user-options", status_code=200)
def get_user_options(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        # Get user from token
        user = get_user_from_token(token, db)

        # Fetch user options from the database
        user_options = db.query(UserOptions).filter(UserOptions.userUuid == user.uuid).first()
        if not user_options:
            raise HTTPException(status_code=404, detail="UserOptions not found for this user.")

        # Return the user options as a dictionary
        return {
                "email": user.email,
                "gender": user_options.gender,
                "height": user_options.height,
                "weight": user_options.weight,
                "weightGoal": user_options.weightGoal,
                "activityLevel": user_options.activityLevel,
                "calorieIntake": user_options.caloriesIntake,
                "age": user_options.age

        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def saveOrUpdateUserMacros(db, user, user_macros):
    # Check if UserMacros already exist
    existing_user_macros = db.query(UserMacros).filter(UserMacros.userUuid == user.uuid).first()
    if existing_user_macros:
        # Update existing UserMacros
        existing_user_macros.calories = user_macros.calories
        existing_user_macros.proteins = user_macros.proteins
        existing_user_macros.fats = user_macros.fats
        existing_user_macros.carbs = user_macros.carbs
    else:
        # Create new UserMacros
        new_user_macros = UserMacros(
            userUuid=user.uuid,
            calories=user_macros.calories,
            proteins=user_macros.proteins,
            fats=user_macros.fats,
            carbs=user_macros.carbs
        )
        db.add(new_user_macros)
    # Commit changes to the database
    db.commit()
