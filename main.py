from fastapi import FastAPI

from lib.controllers.UserOptionsController import router
from lib.controllers.AuthController import authRouter
from lib.database.config import get_db

app = FastAPI()

app.include_router(router, prefix="/api", tags=["UserOptions"])
app.include_router(authRouter, prefix="/api", tags=["Auth"])

print(get_db)

@app.get("/")
def read_root():
    return {"message": "Welcome to the API!"}
