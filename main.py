from fastapi import FastAPI

from lib.controllers.UserMacrosController import userMacrosRouter
from lib.controllers.UserMealsController import userMealsRouter
from lib.controllers.UserOptionsController import userOptionsRouter
from lib.controllers.UserWaterIntakeController import userWaterIntakesRouter
from lib.controllers.UserWeightController import userWeightRouter
from lib.controllers.AuthController import authRouter
from lib.controllers.RecipesController import recipesRouter

app = FastAPI()

app.include_router(authRouter, prefix="/api", tags=["Auth"])
app.include_router(userOptionsRouter, prefix="/api", tags=["UserOptions"])
app.include_router(userMacrosRouter, prefix="/api", tags=["UserMacros"])
app.include_router(userMealsRouter, prefix="/api", tags=["UserMeals"])
app.include_router(userWaterIntakesRouter, prefix="/api", tags=["UserWaterIntakes"])
app.include_router(userWeightRouter, prefix="/api", tags=["UserWeights"])
app.include_router(recipesRouter, prefix="/api", tags=["Recipes"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the API!"}
