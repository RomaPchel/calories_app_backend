from fastapi import FastAPI

from lib.controllers.UserMacrosController import userMacrosRouter
from lib.controllers.UserOptionsController import userOptionsRouter
from lib.controllers.AuthController import authRouter
from lib.database.config import get_db

app = FastAPI()

app.include_router(authRouter, prefix="/api", tags=["Auth"])
app.include_router(userOptionsRouter, prefix="/api", tags=["UserOptions"])
app.include_router(userMacrosRouter, prefix="/api", tags=["UserMacros"])

print(get_db)

@app.get("/")
def read_root():
    return {"message": "Welcome to the API!"}
