from fastapi import HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from lib.database.models import User


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