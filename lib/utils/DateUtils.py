from datetime import date, datetime

from fastapi import HTTPException


def get_dates(day):
    try:
        target_date = date.fromisoformat(day)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use 'YYYY-MM-DD'.")

        # Calculate start and end of the day
    start_of_day = datetime.combine(target_date, datetime.min.time())  # 00:00:00 of the target date
    end_of_day = datetime.combine(target_date, datetime.max.time())  # 23:59:59 of the target date

    return start_of_day, end_of_day
