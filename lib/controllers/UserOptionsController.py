from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy.orm import Session

from lib.database.config import get_db
from lib.database.models import UserOptions, User

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
class UserOptionsSchema(BaseModel):
    gender: str
    height: str
    weight: str
    weightGoal: str
    activityLevel: str
    age: str

@router.post("/save-user-options", status_code=201)
def save_user_options(user_options: UserOptionsSchema, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        print(token)

        # Get user from token
        user = get_user_from_token(token, db)

        # Check if user options already exist for this user
        existing_user_options = db.query(UserOptions).filter(UserOptions.userUuid == user.uuid).first()
        if existing_user_options:
            raise HTTPException(status_code=400, detail="UserOptions already exist for this user.")

        # Create new user options
        print(user)
        new_user_options = UserOptions(
            userUuid=user.uuid,  # Use the UUID of the user from the database
            gender=user_options.gender,
            height=user_options.height,
            weight=user_options.weight,
            weightGoal=user_options.weightGoal,
            activityLevel=user_options.activityLevel,
            age=user_options.age
        )

        # Add to DB and commit
        db.add(new_user_options)
        db.commit()
        db.refresh(new_user_options)

        return {"message": "UserOptions saved successfully", "data": user_options.dict()}

    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



def get_user_from_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, "super-secret-access-token-key", algorithms=["HS256"])
        print(payload)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=403, detail="Could not validate credentials")

        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return user
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
