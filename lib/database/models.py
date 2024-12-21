import enum

from sqlalchemy import (
    Column, String, Float, Date, Enum, ForeignKey, Boolean, BigInteger, Integer
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'User'  # Ensure this matches the table name in the database

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


class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"


class WeightGoal(enum.Enum):
    LOSE = "lose",
    KEEP = "keep",
    GAIN = "gain",


class ActivityLevel(enum.Enum):
    SEDENTARY = "sedentary",
    LOW_ACTIVE = "low_active",
    ACTIVE = "active",
    VERY_ACTIVE = "very_active",


class UserOptions(Base):
    __tablename__ = 'UserOptions'

    userUuid = Column(String, ForeignKey('User.uuid'), primary_key=True)  # Correct ForeignKey reference
    gender = Column(Enum(Gender), nullable=False)
    height = Column(Integer)
    weight = Column(Float)
    weightGoal = Column(Enum(WeightGoal), nullable=False)
    activityLevel = Column(Enum(ActivityLevel), nullable=False)
    age = Column(Integer)

    user = relationship("User", back_populates="user_options")

class UserMacros(Base):
    __tablename__ = 'UserMacros'

    userUuid = Column(String, ForeignKey('User.uuid'), primary_key=True)  # Correct ForeignKey reference
    calories = Column(BigInteger)
    proteins = Column(BigInteger)
    carbs = Column(BigInteger)
    fats = Column(BigInteger)

    user = relationship("User", back_populates="user_macros")

class UserWeight(Base):
    __tablename__ = 'UserWeight'

    userUuid = Column(String, ForeignKey('User.uuid'), primary_key=True)  # Correct ForeignKey reference
    weight = Column(Float)
    date = Column(Date, primary_key=True)

    user = relationship("User", back_populates="user_weights")

class WaterIntake(Base):
    __tablename__ = 'WaterIntake'

    uuid = Column(BigInteger, primary_key=True, autoincrement=True)
    currentIntake = Column(Integer)
    date = Column(Date)

    userUuid = Column(String, ForeignKey('User.uuid'))  # Correct ForeignKey reference
    user = relationship("User", back_populates="water_intake")

class Recipe(Base):
    __tablename__ = 'Recipe'

    uuid = Column(String, primary_key=True)
    proteins = Column(BigInteger)
    fats = Column(BigInteger)
    calories = Column(BigInteger)
    carbs = Column(BigInteger)
    title = Column(String)
    cookingTime = Column(String)
    mealType = Column(Enum("Breakfast", "Lunch", "Dinner", "Snack", name="mealtype"))

    favourite_recipes = relationship("FavouriteRecipes", back_populates="recipe")

class MealType(enum.Enum):
    Breakfast = "breakfast"
    Lunch = "lunch"
    Dinner = "dinner"
    Snack = "snack"

class Meal(Base):
    __tablename__ = 'Meal'

    uuid = Column(String, primary_key=True)  # UUID
    title = Column(String)
    fats = Column(BigInteger)
    proteins = Column(BigInteger)
    calories = Column(BigInteger)
    carbs = Column(BigInteger)
    mealType = Column(Enum(MealType), nullable=False)
    weight = Column(BigInteger)
    date = Column(Date)

    userUuid = Column(String, ForeignKey('User.uuid'))  # Correct ForeignKey reference
    user = relationship("User", back_populates="meal")

class FavouriteRecipes(Base):
    __tablename__ = 'FavouriteRecipes'

    uuid = Column(String, primary_key=True)  # UUID
    userUuid = Column(String, ForeignKey('User.uuid'))  # Correct ForeignKey reference
    recipeUuid = Column(String, ForeignKey('Recipe.uuid'))

    user = relationship("User", back_populates="favourite_recipes")
    recipe = relationship("Recipe", back_populates="favourite_recipes")
