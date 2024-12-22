from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy.orm import Session

from lib.controllers.UserOptionsController import get_user_from_token
from lib.database.config import get_db
from lib.database.models import UserOptions, User, Recipe

recipesRouter = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
class UserOptionsSchema(BaseModel):
    gender: str
    height: str
    weight: str
    weightGoal: str
    activityLevel: str
    age: str

@recipesRouter.get("/recipes", status_code=200)
def get_recipes( db: Session = Depends(get_db)):
    recipes = db.query(Recipe).all()

    if not recipes:
        return []

    return recipes



