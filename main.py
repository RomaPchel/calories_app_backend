from fastapi import FastAPI

from lib.controllers.UserOptionsController import router

app = FastAPI()

app.include_router(router, prefix="/api", tags=["UserOptions"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the API!"}
