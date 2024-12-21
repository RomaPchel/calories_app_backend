from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from lib.database.config import get_db
from lib.database.models import UserMacros, UserOptions
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


@userMacrosRouter.get("/get-water-intake", status_code=200)
def get_water_intake(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        # Get user from token
        user = get_user_from_token(token, db)

        # Retrieve UserOptions for the user
        user_options = db.query(UserOptions).filter(UserOptions.userUuid == user.uuid).first()
        if not user_options:
            raise HTTPException(status_code=404, detail="UserOptions not found for this user.")

        water_intake = calculate_water_intake(user_options)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
