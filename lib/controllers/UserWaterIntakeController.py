import uuid
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from lib.database.config import get_db
from lib.database.models import UserOptions, WaterIntake
from lib.utils.UserUtils import get_user_from_token

waterIntakeRouter = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserWaterSchema(BaseModel):
    ml: int


@waterIntakeRouter.post("/add_water_intake")
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


@waterIntakeRouter.delete("/delete_water_intake/{water_intake_id}")
def delete_water_intake(water_intake_id: uuid, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
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


@waterIntakeRouter.get("/get_water_intakes")
def get_water_intakes(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
):
    try:
        # Get user from token
        user = get_user_from_token(token, db)

        # Validate and parse the start_date and end_date if provided
        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use 'YYYY-MM-DD'")
        else:
            parsed_start_date = None

        if end_date:
            try:
                parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use 'YYYY-MM-DD'")
        else:
            parsed_end_date = None

        # Fetch water intakes based on date range
        if parsed_start_date and parsed_end_date:
            # If both start_date and end_date are provided, filter by the range
            water_intakes = db.query(WaterIntake).filter(
                WaterIntake.userUuid == user.uuid,
                WaterIntake.date >= parsed_start_date,
                WaterIntake.date <= parsed_end_date
            ).all()
        elif parsed_start_date:
            # If only start_date is provided, filter from that date onwards
            water_intakes = db.query(WaterIntake).filter(
                WaterIntake.userUuid == user.uuid,
                WaterIntake.date >= parsed_start_date
            ).all()
        elif parsed_end_date:
            # If only end_date is provided, filter up to that date
            water_intakes = db.query(WaterIntake).filter(
                WaterIntake.userUuid == user.uuid,
                WaterIntake.date <= parsed_end_date
            ).all()
        else:
            # If no date range is provided, get all water intakes
            water_intakes = db.query(WaterIntake).filter(WaterIntake.userUuid == user.uuid).all()

        if not water_intakes:
            raise HTTPException(status_code=404, detail="No water intake records found")

        # Return the list of water intakes
        return {"data": water_intakes}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
