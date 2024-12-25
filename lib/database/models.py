import enum
from sqlalchemy import (
    Column, String, Float, Date, Enum, ForeignKey, Boolean, BigInteger, Integer
)
from sqlalchemy.orm import relationship
from lib.database.config import Base


class Gender(enum.Enum):
    MALE = "Чоловік"
    FEMALE = "Жінка"


class WeightGoal(enum.Enum):
    LOSE = "Втратити вагу",
    KEEP = "Підтримувати нинішню вагу",
    GAIN = "Набрати вагу",


class ActivityLevel(enum.Enum):
    SEDENTARY = "sedentary",
    LOW_ACTIVE = "low_active",
    ACTIVE = "active",
    VERY_ACTIVE = "very_active",


class User(Base):
    __tablename__ = 'User'

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


class UserMeals(Base):
    __tablename__ = 'UserMeals'

    uuid = Column(String, primary_key=True)
    userUuid = Column(String, ForeignKey('User.uuid'))
    mealUuid = Column(String, ForeignKey('Meal.uuid'))
    date = Column(Date)

    user = relationship("User", back_populates="user_meals")
    meal = relationship("Meal", back_populates="user_meals")


class UserOptions(Base):
    __tablename__ = 'UserOptions'

    userUuid = Column(String, ForeignKey('User.uuid'), primary_key=True)
    gender = Column(String)
    height = Column(Float)
    weight = Column(Float)
    weightGoal = Column(String)
    activityLevel = Column(String)
    age = Column(Integer)
    caloriesIntake = Column(Integer)

    user = relationship("User", back_populates="user_options")

class UserMacros(Base):
    __tablename__ = 'UserMacros'

    userUuid = Column(String, ForeignKey('User.uuid'), primary_key=True)
    calories = Column(BigInteger)
    proteins = Column(BigInteger)
    carbs = Column(BigInteger)
    fats = Column(BigInteger)

    user = relationship("User", back_populates="user_macros")

class UserWeight(Base):
    __tablename__ = 'UserWeight'

    userUuid = Column(String, ForeignKey('User.uuid'), primary_key=True)
    weight = Column(Float)
    date = Column(Date, primary_key=True)

    user = relationship("User", back_populates="user_weights")

class WaterIntake(Base):
    __tablename__ = 'WaterIntake'

    uuid = Column(BigInteger, primary_key=True, autoincrement=True)
    currentIntake = Column(Integer)
    date = Column(Date)

    userUuid = Column(String, ForeignKey('User.uuid'))
    user = relationship("User", back_populates="water_intake")

class Recipe(Base):
    __tablename__ = 'Recipe'

    uuid = Column(String, primary_key=True)
    proteins = Column(BigInteger)
    fats = Column(BigInteger)
    calories = Column(BigInteger)
    carbs = Column(BigInteger)
    isPopular = Column(Boolean)
    coverImage = Column(String)
    description = Column(String)
    title = Column(String)
    cookingTime = Column(String)
    mealType = Column(String)

    favourite_recipes = relationship("FavouriteRecipes", back_populates="recipe")

class MealType(enum.Enum):
    Breakfast = "breakfast"
    Lunch = "lunch"
    Dinner = "dinner"
    Snack = "snack"

class Meal(Base):
    __tablename__ = 'Meal'

    uuid = Column(String, primary_key=True)
    title = Column(String)
    fats = Column(BigInteger)
    proteins = Column(BigInteger)
    calories = Column(BigInteger)
    carbs = Column(BigInteger)
    mealType = Column(Enum(MealType), nullable=False)
    weight = Column(BigInteger)
    date = Column(Date)

    userUuid = Column(String, ForeignKey('User.uuid'))
    user_meals = relationship("UserMeals", back_populates="meal")

class FavouriteRecipes(Base):
    __tablename__ = 'FavouriteRecipes'

    uuid = Column(String, primary_key=True)
    userUuid = Column(String, ForeignKey('User.uuid'))
    recipeUuid = Column(String, ForeignKey('Recipe.uuid'))

    user = relationship("User", back_populates="favourite_recipes")
    recipe = relationship("Recipe", back_populates="favourite_recipes")
