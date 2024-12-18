from sqlalchemy import (
    Column, String, Float, Date, Enum, ForeignKey, Boolean, BigInteger
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    uuid = Column(String, primary_key=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    registeredAt = Column(Date, nullable=False)

    user_options = relationship("UserOptions", back_populates="user", uselist=False)
    user_macros = relationship("UserMacros", back_populates="user", uselist=False)
    user_weights = relationship("UserWeight", back_populates="user")
    water_intake = relationship("WaterIntake", back_populates="user")
    favourite_recipes = relationship("FavouriteRecipes", back_populates="user")
    user_meals = relationship("UserMeals", back_populates="user")

class UserOptions(Base):
    __tablename__ = 'useroptions'

    userUuid = Column(String, ForeignKey('user.uuid'), primary_key=True)
    gender = Column(String)
    height = Column(String)
    weight = Column(String)
    weightGoal = Column(String)
    goal = Column(String)
    activityLevel = Column(String)
    age = Column(String)

    user = relationship("User", back_populates="user_options")

class UserMacros(Base):
    __tablename__ = 'usermacros'

    userUuid = Column(String, ForeignKey('user.uuid'), primary_key=True)
    calories = Column(BigInteger)
    proteins = Column(BigInteger)
    carbs = Column(BigInteger)
    fats = Column(BigInteger)

    user = relationship("User", back_populates="user_macros")

class UserWeight(Base):
    __tablename__ = 'userweight'

    userUuid = Column(String, ForeignKey('user.uuid'), primary_key=True)
    weight = Column(Float)
    date = Column(Date, primary_key=True)

    user = relationship("User", back_populates="user_weights")

class WaterIntake(Base):
    __tablename__ = 'waterintake'

    uuid = Column(BigInteger, primary_key=True, autoincrement=True)
    goal = Column(Float)
    currentIntake = Column(Float)
    date = Column(Date)

    userUuid = Column(String, ForeignKey('user.uuid'))
    user = relationship("User", back_populates="water_intake")

class Recipe(Base):
    __tablename__ = 'recipe'

    uuid = Column(String, primary_key=True)
    proteins = Column(BigInteger)
    fats = Column(BigInteger)
    calories = Column(BigInteger)
    carbs = Column(BigInteger)
    title = Column(String)
    cookingTime = Column(String)
    mealType = Column(Enum("Breakfast", "Lunch", "Dinner", "Snack", name="mealtype"))

    favourite_recipes = relationship("FavouriteRecipes", back_populates="recipe")

class Meal(Base):
    __tablename__ = 'meal'

    uuid = Column(String, primary_key=True)  # UUID
    title = Column(String)
    fats = Column(BigInteger)
    proteins = Column(BigInteger)
    calories = Column(BigInteger)
    carbs = Column(BigInteger)
    mealType = Column(BigInteger)
    weight = Column(BigInteger)

    user_meals = relationship("UserMeals", back_populates="meal")

class FavouriteRecipes(Base):
    __tablename__ = 'favouriterecipes'

    uuid = Column(String, primary_key=True)  # UUID
    userUuid = Column(String, ForeignKey('user.uuid'))
    recipeUuid = Column(String, ForeignKey('recipe.uuid'))

    user = relationship("User", back_populates="favourite_recipes")
    recipe = relationship("Recipe", back_populates="favourite_recipes")

class UserMeals(Base):
    __tablename__ = 'usermeals'

    uuid = Column(String, primary_key=True)  # UUID
    userUuid = Column(String, ForeignKey('user.uuid'))
    mealUuid = Column(String, ForeignKey('meal.uuid'))
    isCustom = Column(Boolean)

    user = relationship("User", back_populates="user_meals")
    meal = relationship("Meal", back_populates="user_meals")
