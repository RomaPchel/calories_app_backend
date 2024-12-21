import uuid
from datetime import date

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from lib.database.config import get_db
from lib.database.models import UserOptions, WaterIntake
from lib.utils.DateUtils import get_dates
from lib.utils.UserMacrosUtils import calculate_water_intake
from lib.utils.UserUtils import get_user_from_token

userWaterIntakesRouter = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserWaterSchema(BaseModel):
    ml: int


@userWaterIntakesRouter.post("/add_water_intake")
def add_water_intake(water_intake: UserWaterSchema, db: Session = Depends(get_db),
                     token: str = Depends(oauth2_scheme)):
    try:
        print(token)

        # Get user from token
        user = get_user_from_token(token, db)

        # Fetch user options to calculate recommended water intake
        user_options = db.query(UserOptions).filter(UserOptions.userUuid == user.uuid).first()
        if not user_options:
            raise HTTPException(status_code=404, detail="User options not found")

        # Log the water intake
        new_intake = WaterIntake(userUuid=user.uuid,
                                 currentIntake=water_intake.ml,
                                 date=date.today())
        db.add(new_intake)
        db.commit()

        return {"message": "Water intake saved successfully", "data": new_intake}

    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@userWaterIntakesRouter.delete("/delete_water_intake/{water_intake_id}")
def delete_water_intake(water_intake_id: uuid.UUID, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        # Get user from token
        user = get_user_from_token(token, db)

        # Fetch the water intake record by its ID and ensure it belongs to the user
        water_intake = db.query(WaterIntake).filter(WaterIntake.uuid == water_intake_id,
                                                    WaterIntake.userUuid == user.uuid).first()

        if not water_intake:
            raise HTTPException(status_code=404, detail="Water intake record not found")

        # Delete the water intake record
        db.delete(water_intake)
        db.commit()

        return {"message": "Water intake deleted successfully"}

    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()  # Ensure the session is rolled back on error
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@userWaterIntakesRouter.get("/get_water_intakes")
def get_water_intakes(
        day: str,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
):
    try:
        # Get user from token
        user = get_user_from_token(token, db)

        start_of_day, end_of_day = get_dates(day)

        # Query meals for the specific day
        water_intakes = db.query(WaterIntake).filter(
            WaterIntake.userUuid == user.uuid,
            WaterIntake.date >= start_of_day,
            WaterIntake.date <= end_of_day
        ).all()

        return water_intakes

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@userWaterIntakesRouter.get("/recommended-water_intake", status_code=200)
def recommended_water_intake(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        # Get user from token
        user = get_user_from_token(token, db)

        # Fetch user options to calculate recommended water intake
        user_options = db.query(UserOptions).filter(UserOptions.userUuid == user.uuid).first()
        if not user_options:
            raise HTTPException(status_code=404, detail="User options not found")

        water_intake = calculate_water_intake(user_options)

        # Return the recommended macros
        return {
            "message": "Recommended UserMacros calculated successfully",
            "data": {
                "ml": water_intake,
            }
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
