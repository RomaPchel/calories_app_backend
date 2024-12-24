from lib.database.models import UserMacros, ActivityLevel, WeightGoal


def calculate_user_macros(user, user_options):
    # Calculate base calories
    gender_factor = 5 if user_options.gender.lower() == "Чоловік" else -161
    base_calories = int(10 * float(user_options.weight) +
                        6.25 * float(user_options.height) -
                        5 * int(user_options.age) +
                        gender_factor)

    # Adjust for activity level
    activity_multiplier = {
        ActivityLevel.SEDENTARY: 1.2,
        ActivityLevel.LOW_ACTIVE: 1.375,
        ActivityLevel.ACTIVE: 1.55,
        ActivityLevel.VERY_ACTIVE: 1.725
    }

    activity_calories = base_calories * activity_multiplier.get(user_options.activityLevel, 1.2)

    # Adjust for weight goal
    if user_options.weightGoal == WeightGoal.LOSE:
        calories = int(activity_calories * 0.9)  # Reduce by 10% for weight loss
    elif user_options.weightGoal == WeightGoal.GAIN:
        calories = int(activity_calories * 1.1)  # Increase by 10% for weight gain
    else:
        calories = int(activity_calories)  # No change for weight maintenance

    # Calculate macros
    proteins = int(calories * 0.25 / 4)
    fats = int(calories * 0.30 / 9)
    carbs = int(calories * 0.45 / 4)

    return UserMacros(userUuid=user.uuid, calories=calories, proteins=proteins, fats=fats, carbs=carbs)

def calculate_user_intake(user_options):
    # Calculate base calories
    gender_factor = 5 if user_options.gender.lower() == "Чоловік" else -161
    base_calories = int(10 * float(user_options.weight) +
                        6.25 * float(user_options.height) -
                        5 * int(user_options.age) +
                        gender_factor)

    # Adjust for activity level
    activity_multiplier = {
        ActivityLevel.SEDENTARY: 1.2,
        ActivityLevel.LOW_ACTIVE: 1.375,
        ActivityLevel.ACTIVE: 1.55,
        ActivityLevel.VERY_ACTIVE: 1.725
    }

    activity_calories = base_calories * activity_multiplier.get(user_options.activityLevel, 1.2)

    # Adjust for weight goal
    if user_options.weightGoal == WeightGoal.LOSE:
        calories = int(activity_calories * 0.9)  # Reduce by 10% for weight loss
    elif user_options.weightGoal == WeightGoal.GAIN:
        calories = int(activity_calories * 1.1)  # Increase by 10% for weight gain
    else:
        calories = int(activity_calories)  # No change for weight maintenance

    return calories



def calculate_water_intake(user_options):
    # Convert weight to kilograms (if it's in pounds)
    weight_in_kg = float(user_options.weight) / 2.2 if user_options.weight else 0

    # Calculate base water intake (30-35 mL per kg of body weight)
    base_water_intake = weight_in_kg * 30  # 30 mL per kg

    # Adjust for activity level
    activity_adjustments = {
        ActivityLevel.SEDENTARY: 0,
        ActivityLevel.LOW_ACTIVE: 250,  # Add 250 mL for low activity
        ActivityLevel.ACTIVE: 500,  # Add 500 mL for active
        ActivityLevel.VERY_ACTIVE: 1000,  # Add 1L for very active
    }

    # Adjust the water intake based on activity level
    water_intake = base_water_intake + activity_adjustments.get(user_options.activityLevel, 0)

    return int(water_intake)  # Return the final water intake in mL

