import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends
from jose import jwt
from passlib.hash import bcrypt
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from lib.database.config import get_db
from lib.database.models import User

SECRET_KEY = "super-secret-access-token-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

authRouter = APIRouter()

class RegisterSchema(BaseModel):
    email: EmailStr
    password: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class TokenSchema(BaseModel):
    accessToken: str
    token_type: str

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@authRouter.post("/register", response_model=TokenSchema, status_code=201)
def register(user_data: RegisterSchema, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")

    hashed_password = bcrypt.hash(user_data.password)
    new_user_uuid = str(uuid.uuid4())

    new_user = User(
        uuid=new_user_uuid,
        email=user_data.email,
        password=hashed_password,
        registeredAt=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"sub": new_user.email})
    return {"accessToken": access_token, "token_type": "bearer"}

@authRouter.post("/login", response_model=TokenSchema)
def login(user_data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not bcrypt.verify(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Encode both email and user UUID in the JWT token (convert UUID to string)
    access_token = create_access_token(data={"sub": user.email, "uuid": str(user.uuid)})
    print(access_token)
    return {"accessToken": access_token, "token_type": "bearer"}
